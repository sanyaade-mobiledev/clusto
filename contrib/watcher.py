from socket import socket, AF_INET, SOCK_DGRAM
from traceback import format_exc
from multiprocessing import Process
from threading import Thread
from Queue import Queue
from time import strftime, time, localtime, sleep
from struct import unpack

from scapy import SNMP, BOOTP, sniff

from clusto.scripthelpers import init_script
from clusto.drivers import IPManager, PenguinServer
import clusto
import sys

from discovery import SWITCHPORT_TO_RU, RU_TO_PWRPORT

def update_clusto(trap):
    ts = strftime('[%Y-%m-%d %H:%M:%S]')
    if trap['operation'] != 1:
        return

    switch = IPManager.get_device(trap['switch'])
    if not switch:
        print ts, "Trap received from a device that clusto doesn't know about", trap['switch']
        return
    else:
        switch = switch[0]
        #print 'Got trap from', switch.name

    if trap['port'] > 20:
        return

    if not switch.attrs(key='snmp', subkey='discovery', value=1):
        return

    server = switch.port_info['nic-eth'][trap['port']]['connection']
    if not server:
        servernames = clusto.get_by_name('servernames')
        print ts, 'Allocating new server on', trap['switch'], trap['port']
        server = servernames.allocate(PenguinServer)

    print ts, server.name, repr(trap)

    ru = SWITCHPORT_TO_RU[trap['port']]

    ifnum = int(trap['port'] > 21) + 1

    if not trap['mac'] in server.attr_values(key='bootstrap', subkey='mac', value=trap['mac']):
        print 'Adding bootstrap mac to', server.name
        server.add_attr(key='bootstrap', subkey='mac', value=trap['mac'])

    if server.port_free('nic-eth', ifnum):
        server.connect_ports('nic-eth', ifnum, switch, trap['port'])
    switch.set_port_attr('nic-eth', trap['port'], 'vlan', trap['vlan'])

    if server.port_free('pwr-nema-5', 1):
        power = switch.port_info['pwr-nema-5'][1]['connection']
        server.connect_ports('pwr-nema-5', 1, power, RU_TO_PWRPORT[ru])

    if server.port_free('console-serial', 1):
        ts = switch.port_info['console-serial'][1]['connection']
        server.connect_ports('console-serial', 1, ts, trap['port'])

    rack = [x for x in switch.parents() if x.type == 'rack']
    if rack:
        rack = rack[0]
        if not server in rack:
            rack.insert(server, ru)

    print ts, switch.name, server.name, trap['mac']

def trap_listen():
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind(('0.0.0.0', 162))
    while True:
        data, address = sock.recvfrom(4096)
        trap = SNMP(data)

        for var in trap.PDU.varbindlist:
            if var.oid.val == '1.3.6.1.4.1.9.9.215.1.1.8.1.2.1':
                var.value.val = var.value.val[:11]
                operation, vlan, mac, port = unpack('>cH6sH', var.value.val)
                result = {
                    'operation': ord(operation),
                    'vlan': vlan,
                    'mac': ':'.join([('%x' % ord(x)).ljust(2, '0') for x in mac]).lower(),
                    'port': port,
                    'switch': address[0],
                }
                yield result

dhcpqueue = Queue()

def dhcp_parse(packet):
    options = packet[BOOTP].payload.options

    mac = None
    vendor = None
    options = [(k, v) for k, v in [x for x in options if type(x) == tuple]]
    options = dict(options)
    if 'client_id' in options:
        mac = unpack('>6s', options['client_id'][1:])[0]
        options['client_id'] = ':'.join([('%x' % ord(x)).ljust(2, '0') for x in mac]).lower()
    dhcpqueue.put((packet.src, options))

def dhcp_listen():
    sniff(filter='udp port 67', prn=lambda x: dhcp_parse(x), store=0)

def run_snmp():
    init_script()

    for trap in trap_listen():
        try:
            clusto.begin_transaction()
            update_clusto(trap)
            clusto.commit()
        except:
            print 'Exception in run_snmp process'
            print format_exc()
            clusto.rollback_transaction()

def run_dhcp():
    init_script()

    t = Thread(target=dhcp_listen)
    t.setDaemon(True)
    t.start()

    while True:
        try:
            dhcp_process()
        except:
            print format_exc()
            print 'dhcp_process threw an exception, lost an update'

def dhcp_process():
    address, request = dhcpqueue.get()

    if 'client_id' in request and (request['client_id'].lower() != address.lower()):
        pass
        #print 'Warning: DHCP client ID does not match source MAC', request['client_id'], '!=', address
    address = request.get('client_id', address).lower()

    server = clusto.get_entities(attrs=[{
            'key': 'bootstrap',
            'subkey': 'mac',
            'value': address
        }, {
            'key': 'port-nic-eth',
            'subkey': 'mac',
            'number': 1,
            'value': address
        }])
    if not server:
        #print 'DHCP from unknown MAC:', address
        return

    try:
        server = server[0]
        if request.get('vendor_class_id', None) == 'udhcp 0.9.9-pre':
            # This is an IPMI request
            print 'Associating IPMI address', address, 'with nic-eth:1 on', server.name
            server.set_port_attr('nic-eth', 1, 'ipmi-mac', address)
        else:
            print 'Associating physical address with nic-eth:1 on', server.name
            server.set_port_attr('nic-eth', 1, 'mac', address)
    except:
        print 'Something went wrong'
        print format_exc()

def main():
    t1 = Process(target=run_dhcp)
    t1.start()

    try:
        run_snmp()
    except KeyboardInterrupt:
        t1.terminate()
        t1.join()

if __name__ == '__main__':
    #main()
    if sys.argv[1] == 'dhcp':
        run_dhcp()
        sys.exit(0)

    if sys.argv[1] == 'snmp':
        run_snmp()
        sys.exit(0)

    print 'Usage: %s (dhcp|snmp)' % sys.argv[0]
