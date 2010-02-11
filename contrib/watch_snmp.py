#!/home/synack/src/clusto/env/bin/python
from socket import socket, AF_INET, SOCK_DGRAM
from traceback import format_exc
from time import strftime, time, localtime, sleep
from struct import unpack

import logging
runtime = logging.getLogger('scapy.runtime')
runtime.setLevel(logging.ERROR)
from scapy.all import SNMP

from clusto.scripthelpers import init_script
from clusto.drivers import IPManager, PenguinServer
import clusto

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

    if not switch.attrs(key='snmp', subkey='discovery', value=1, merge_container_attrs=True):
        print 'Discovery disabled for', switch.name
        return

    server = switch.get_connected('nic-eth', trap['port'])
    if not server:
        servernames = clusto.get_by_name('servernames')
        print ts, 'Allocating new server on', trap['switch'], trap['port']
        server = servernames.allocate(PenguinServer)

    print ts, server.name, repr(trap)

    ru = SWITCHPORT_TO_RU[trap['port']]

    ifnum = int(trap['port'] > 21) + 1

    clusto.begin_transaction()
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
    clusto.commit()

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

def main():
    for trap in trap_listen():
        try:
            update_clusto(trap)
        except:
            print 'Exception in run_snmp process'
            print format_exc()

if __name__ == '__main__':
    init_script()
    main()
