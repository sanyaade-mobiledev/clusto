#!/usr/bin/env python
from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_REUSEADDR, SO_BROADCAST, gethostbyname, gethostname
from traceback import format_exc
from struct import unpack

from scapy.layers.dhcp import BOOTP, DHCP, DHCPTypes, DHCPOptions, DHCPRevOptions

from clusto.scripthelpers import init_script
from clusto.drivers import IPManager, PenguinServer
import clusto

SERVER_IP = '10.2.128.48'

DHCPOptions.update({
    66: 'tftp_server',
    67: 'tftp_filename',
})

for k,v in DHCPOptions.iteritems():
    if type(v) is str:
        n = v
        v = None
    else:
        n = v.name
    DHCPRevOptions[n] = (k,v)

class DHCPRequest(object):
    def __init__(self, packet):
        self.packet = packet
        self.parse()

    def parse(self):
        options = self.packet[DHCP].options
        hwaddr = ':'.join(['%02x' % ord(x) for x in self.packet.chaddr[:6]])

        mac = None
        vendor = None
        options = dict([x for x in options if isinstance(x, tuple)])
        if 'client_id' in options:
            mac = unpack('>6s', options['client_id'][1:])[0]
            options['client_id'] = ':'.join(['%02x' % ord(x) for x in mac]).lower()

        self.type = DHCPTypes[options['message-type']]
        self.hwaddr = hwaddr
        self.options = options

class DHCPResponse(object):
    def __init__(self, type, offerip=None, options={}, request=None):
        self.type = type
        self.offerip = offerip
        self.serverip = gethostbyname(gethostname())
        self.options = options
        self.request = request

    def set_type(self, type):
        self.type = type

    def build(self):
        options = [
            ('message-type', self.type)
        ]
        for k, v in self.options.items():
            if k == 'enabled': continue
            if not k in DHCPRevOptions:
                print 'Unknown DHCP option:', k
                continue
            if isinstance(v, unicode):
                v = v.encode('ascii', 'ignore')
            options.append((k, v))

        bootp_options = {
            'op': 2,
            'xid': self.request.packet.xid,
            'ciaddr': self.offerip,
            'yiaddr': self.offerip,
            'chaddr': self.request.packet.chaddr,
        }
        if 'tftp_server' in self.options:
            bootp_options['siaddr'] = self.options['tftp_server']
        if 'tftp_filename' in self.options:
            bootp_options['file'] = self.options['tftp_filename']
        for k, v in bootp_options.items():
            if isinstance(v, unicode):
                bootp_options[k] = v.encode('ascii', 'ignore')

        pkt = BOOTP(**bootp_options)/DHCP(options=options)
        pkt.show()
        return pkt

class DHCPServer(object):
    def __init__(self, bind_address=('0.0.0.0', 67)):
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sock.bind(bind_address)
        self.sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server_id = gethostbyname(gethostname())

    def run(self):
        while True:
            data, address = self.sock.recvfrom(4096)
            packet = BOOTP(data)
            request = DHCPRequest(packet)

            #print request.type, request.hwaddr

            methodname = 'handle_%s' % request.type
            if hasattr(self, methodname):
                method = getattr(self, methodname)
                method(request)

    def send(self, address, data):
        while data:
            bytes = self.sock.sendto(str(data), 0, (address, 68))
            data = data[bytes:]

class ClustoDHCPServer(DHCPServer):
    def __init__(self):
        DHCPServer.__init__(self)
        self.offers = {}

    def handle_request(self, request):
        chaddr = request.packet.chaddr
        if not chaddr in self.offers:
            print 'Got a request before sending an offer from', request.hwaddr
            return
        response = self.offers[chaddr]
        response.type = 'ack'

        self.send('255.255.255.255', response.build())

    def handle_discover(self, request):
        self.update_ipmi(request)

        server = clusto.get_entities(attrs=[{
            'key': 'port-nic-eth',
            'subkey': 'mac',
            'number': 1,
            'value': request.hwaddr,
        }])

        if not server:
            #print 'Request from unknown device:', request.hwaddr
            return

        if len(server) > 1:
            print 'More than one server with address %s: %s' % (request.hwaddr, ', '.join([x.name for x in server]))
            return
        
        server = server[0]

        if not server.attrs(key='dhcp', subkey='enabled', value=1, merge_container_attrs=True):
            print 'DHCP not enabled for', server.name
            return

        ip = server.get_ips()
        if not ip:
            print 'No IP assigned for', server.name
            return
        else:
            ip = ip[0]

        ipman = IPManager.get_ip_manager(ip)

        options = {
            'server_id': self.server_id,
            'lease_time': 3600,
            'renewal_time': 1600,
            'subnet_mask': ipman.netmask,
            'broadcast_address': ipman.ipy.broadcast().strNormal(),
            'router': ipman.gateway,
            'hostname': server.name,
        }

        for attr in server.attrs(key='dhcp', merge_container_attrs=True):
            options[attr.subkey] = attr.value

        response = DHCPResponse(type='offer', offerip=ip, options=options, request=request)
        self.offers[request.packet.chaddr] = response
        self.send('255.255.255.255', response.build())

    def update_ipmi(self, request):
        server = clusto.get_entities(attrs=[{
            'key': 'bootstrap',
            'subkey': 'mac',
            'value': request.hwaddr,
        }, {
            'key': 'port-nic-eth',
            'subkey': 'mac',
            'number': 1,
            'value': request.hwaddr,
        }])

        if not server:
            return

        try:
            server = server[0]
            if request.options.get('vendor_class_id', None) == 'udhcp 0.9.9-pre':
                # This is an IPMI request
                #print 'Associating IPMI address', request.hwaddr, 'with nic-eth:1 on', server.name
                server.set_port_attr('nic-eth', 1, 'ipmi-mac', request.hwaddr)
            else:
                #print 'Associating physical address with nic-eth:1 on', server.name
                server.set_port_attr('nic-eth', 1, 'mac', request.hwaddr)
        except:
            print 'Error updating server MAC:', format_exc()

if __name__ == '__main__':
    init_script()
    server = ClustoDHCPServer()
    server.run()
