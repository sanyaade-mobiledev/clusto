#!/usr/bin/env python
from socket import socket, AF_INET, SOCK_DGRAM
from traceback import format_exc
from time import strftime, time, localtime, sleep
from struct import unpack
import sys

import logging

log = logging.getLogger('clusto.snmp')
fmt = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s', '%Y-%m-%d %H:%M:%S')
handler = logging.FileHandler('/var/log/clusto.log')
handler.setFormatter(fmt)
log.addHandler(handler)
log.setLevel(logging.INFO)

runtime = logging.getLogger('scapy.runtime')
runtime.setLevel(logging.ERROR)

from scapy.all import SNMP

from clusto.scripthelpers import init_script
from clusto.drivers import IPManager, PenguinServer
import clusto

import rackfactory

def update_clusto(trap):
    ts = strftime('[%Y-%m-%d %H:%M:%S]')
    if trap['operation'] != 1:
        return

    switch = IPManager.get_devices(trap['switch'])
    if not switch:
        log.warning('Unknown trap source: %s' % trap['switch'])
        return
    else:
        switch = switch[0]

    if not switch.attrs(key='snmp', subkey='discovery', value=1, merge_container_attrs=True):
        log.debug('key=snmp, subkey=discovery for %s not set to 1, ignoring trap' % switch.name)
        return

    server = switch.get_connected('nic-eth', trap['port'])
    if not server:
        servernames = clusto.get_by_name('servernames')
        clusto.SESSION.clusto_description = 'SNMP allocate new server'
        server = servernames.allocate(PenguinServer)
        log.info('Created new server on %s port %s: %s' % (trap['switch'], trap['port'], server.name))

    rack = switch.parents(clusto_types=['rack'])[0]

    try:
        factory = rackfactory.get_factory(rack.name)
    except:
        log.error(format_exc())
        return

    try:
        clusto.begin_transaction()
        if not trap['mac'] in server.attr_values(key='bootstrap', subkey='mac', value=trap['mac']):
            log.debug('Adding bootstrap mac to', server.name)
            server.add_attr(key='bootstrap', subkey='mac', value=trap['mac'])

        factory.add_server(server, trap['port'])
        switch.set_port_attr('nic-eth', trap['port'], 'vlan', trap['vlan'])

        clusto.SESSION.clusto_description = 'SNMP update MAC and connections on %s' % server.name
        clusto.commit()
    except:
        log.error(format_exc())
        clusto.rollback_transaction()

    log.debug(repr(trap))

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
                    'mac': ':'.join([('%x' % ord(x)).rjust(2, '0') for x in mac]).lower(),
                    'port': port,
                    'switch': address[0],
                }
                yield result

def main():
    for trap in trap_listen():
        try:
            update_clusto(trap)
        except:
            log.error('Exception in run_snmp process')
            log.error(format_exc())

if __name__ == '__main__':
    log.info('Clusto SNMP server starting')
    init_script()
    sys.exit(main())
