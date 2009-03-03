from clusto.drivers import BasicDatacenter, BasicRack, BasicServer, BasicNetworkSwitch, PowerTowerXM, SimpleEntityNameManager
from clusto.scripthelpers import getClustoConfig
import clusto

from traceback import format_exc
from subprocess import Popen, PIPE
from xml.etree import ElementTree
from pprint import pprint
import yaml
import socket
import sys

SWITCHPORT_TO_RU = {
    1:1, 2:2, 3:3, 4:4, 5:5,
    6:7, 7:8, 8:9, 9:10, 10:11,
    11:13, 12:14, 13:15, 14:16, 15:17,
    16:19, 17:20, 18:21, 19:22, 20:23,

    21:1, 22:2, 23:3, 24:4, 25:5,
    26:7, 27:8, 28:9, 29:10, 30:11,
    31:13, 32:14, 33:15, 34:16, 35:17,
    36:19, 37:20, 38:21, 39:22, 40:23,
}

RU_TO_PWRPORT = {
    1: 'bb1',
    2: 'bb2',
    3: 'bb3',
    4: 'bb4',
    5: 'bb5',
    
    7: 'ba1',
    8: 'ba2',
    9: 'ba3',
    10: 'ba4',
    11: 'ba5',

    13: 'ab1',
    14: 'ab2',
    15: 'ab3',
    16: 'ab4',
    17: 'ab5',

    18: 'aa1',
    19: 'aa2',
    20: 'aa3',
    21: 'aa4',
    22: 'aa5',

    30: 'ab8',
    31: 'aa8',
    
    33: 'aa6',
    34: 'ba6',
    35: 'aa7',
    36: 'ba7',
}

def get_or_create(objtype, name):
    try:
        return clusto.getByName(name)
    except LookupError:
        return objtype(name)

def get_snmp_hostname(ipaddr, community='digg1t'):
    proc = Popen(['scli', '-c', 'show system info', '-x', ipaddr, community], stdout=PIPE)
    xmldata = proc.stdout.read()
    xmltree = ElementTree.fromstring(xmldata)
    hostname = list(xmltree.getiterator('name'))
    if len(hostname) > 0:
        hostname = hostname[0].text
    else:
        hostname = None
    return hostname

def get_ssh_hostname(ipaddr, username='root'):
    proc = Popen(['ssh', '%s@%s' % (username, ipaddr), 'hostname'], stdout=PIPE)
    output = proc.stdout.read()
    return output.rstrip('\r\n')

def get_hostname(ipaddr):
    hostname = get_snmp_hostname(ipaddr)
    if not hostname:
        try:
            hostname = getfqdn(ipaddr)
        except: pass
    if not hostname:
        try:
            hostname = get_ssh_hostname(ipaddr)
        except: pass
    hostname = hostname.split('.', 1)[0]
    return hostname

def discover_interfaces(ipaddr, server=None, ssh_user='root'):
    if not server:
        server = get_server(ipaddr)
    proc = Popen(['ssh', '-o', 'StrictHostKeyChecking no', '%s@%s' % (ssh_user, ipaddr), '/sbin/ip addr show up'], stdout=PIPE)
    output = proc.stdout.read()
    iface = {}
    for line in output.split('\n'):
        line = line.rstrip('\r\n')
        if line[0].isdigit():
            num, line = line.split(':', 1)
            iface[num] = []
        iface[num].append(line.strip())

    patterns = [
        re.compile('^(?P<name>[a-Z0-9]+): \<(?P<flags>[A-Z0-9,]+)\> mtu (?P<mtu>[0-9]+) (?P<linkflags>.*)$'),
        re.compile('^link/(?P<linktype>[a-z]+) (?P<mac>[a-Z0-9:]+) brd (?P<broadcastmac>[a-Z0-9:]+)$'),
        re.compile('^inet (?P<ip>[0-9.]+)/(?P<netmask>[0-9]+) brd (?P<broadcastip>[0-9.]+) (?P<v4flags>.*)$'),
        re.compile('^inet6 (?P<ip6>[a-Z0-9:]+)/(?P<netmask6>[0-9]+) scope (?P<scope6>[\w]+)$')
    ]
    ifdict = {}
    for num in iface:
        ifdict[num] = {}
        for line in iface[num]:
            for pattern in patterns:
                match = pattern.match(line)
                if match:
                    ifdict[num].update(match.groupdict())
                    break
            if not match:
                if not 'extra' in ifdict[num]:
                    ifdict[num]['extra'] = ''
                ifdict[num]['extra'] += line

    pprint(ifdict)
    return

def get_server(ipaddr, fqdn_base='digg.internal'):
    server = None
    fqdn = None

    names = get_or_create(SimpleEntityNameManager, 'servernames')
    hostname = get_hostname(ipaddr)
    if hostname:
        if hostname.endswith(fqdn_base):
            fqdn = hostname
        hostname = hostname.split('.', 1)[0]

        try:
            server = clusto.getByName(hostname)
        except LookupError:
            print "Server %s doesn't exist in clusto... Creating it"
            server = names.allocate(BasicServer, hostname)
    else:
        print 'Unable to determine hostname for %s... Assuming this is a new server' % ipaddr
        server = names.allocate(BasicServer)

    if fqdn:
        server.addFQDN(fqdn)

    return server

def import_ipmac(name, macaddr, ipaddr, portnum):
    '''
    Insert or update a server in clusto
    '''

    # Get the basic datacenter, rack, and switch objects
    portnum = int(portnum)
    n = name.split('-', 3)
    switch_name = '-'.join(n)
    rack_name = '-'.join(n[:-1])
    dc_name = n[:-2][0]

    dc = get_or_create(BasicDatacenter, dc_name)
    rack = get_or_create(BasicRack, rack_name)
    switch = get_or_create(BasicNetworkSwitch, switch_name)
    pwr = get_or_create(PowerTowerXM, '%s-pwr1' % rack_name)

    if not rack in dc:
        dc.insert(rack)
    if not switch in rack:
        rack.insert(switch, 31)
    if not pwr in rack:
        rack.insert(pwr, (28, 29))

    # Query clusto for a device matching the mac address.
    #server = None
    server = None
    hostname = get_hostname(ipaddr)
    if hostname:
        try:
            server = clusto.getByName(hostname)
        except LookupError:
            try:
                mgr = clusto.getByName('servernames')
                mgr = SimpleEntityNameManager('servernames')
            except:
                # TODO: Finish this.
                pass

    if not server:
        for dev in rack.contents():
            ru = rack.getRackAndU(dev)['RU'][0]
            if ru == SWITCHPORT_TO_RU[portnum]:
                server = dev
                break
    if not server:
        try:
            namemgr = clusto.getByName('servernames')
        except:
            namemgr = SimpleEntityNameManager('servernames', basename='s', digits=4)
        server = namemgr.allocate(BasicServer)

    if not server in rack:
        rack.insert(server, SWITCHPORT_TO_RU[portnum])

    if portnum < 21:
        ifnum = 0
    else:
        ifnum = 1

    server.setPortAttr('MACAddress', macaddr, 'nic-eth', ifnum)
    if not server.portFree('nic-eth', ifnum):
        if not server.getConnected('nic-eth', ifnum) == switch:
            server.disconnectPort('nic-eth', ifnum)
            server.connectPorts('nic-eth', ifnum, switch, portnum)
    else:
        server.connectPorts('nic-eth', ifnum, switch, portnum)

    if server.portFree('pwr-nema-5', 0):
        ru = rack.getRackAndU(server)['RU'][0]
        server.connectPorts('pwr-nema-5', 0, pwr, RU_TO_PWRPORT[ru])
    
    iplist = [x.value for x in server.attrs('ip-address')]
    if not ipaddr in iplist:
        server.addAttr('ip-address', ipaddr)

    names = []
    try:
        names = getfqdn(ipaddr)
    except: pass

    try:
        names.append(get_snmp_hostname(ipaddr))
    except: pass

    namelist = [x.value for x in server.attrs('hostname')]
    for hostname in names:
        if not hostname in namelist:
            server.addAttr('hostname', hostname)

    #ipnet = IPManager('sjc1-internal-network', gateway='10.2.128.1', netmask='255.255.252.0', baseip='

    clusto.commit()
    pprint(server)

def main():
    if len(sys.argv) > 1:
        if not exists(sys.argv[1]):
            print 'File %s does not exist.' % sys.argv[1]
            return
        fd = file(sys.argv[1], 'r')
    else:
        fd = sys.stdin

    for line in fd.readlines():
        switch, macaddr, ipaddr, port = line.rstrip('\n').split(';', 3)
        try:
            import_ipmac(switch, macaddr, ipaddr, port)
        except:
            print format_exc()
    #pprint(clusto.getEntities())

if __name__ == '__main__':
    config = getClustoConfig()
    clusto.connect(config.get('clusto', 'dsn'))
    clusto.initclusto()
    main()
