from clusto.drivers import BasicDatacenter, BasicRack, BasicServer, BasicVirtualServer, BasicNetworkSwitch, PowerTowerXM, IPManager, OpenGearCM4148
from clusto.scripthelpers import getClustoConfig
import clusto

from traceback import format_exc
from subprocess import Popen, PIPE, STDOUT
from xml.etree import ElementTree
from os.path import exists
from pprint import pprint
import yaml
import socket
import sys
import re

from discovery import *

def get_environment(dc, rack, switch):
    dc = get_or_create(BasicDatacenter, dc)
    rack = get_or_create(BasicRack, rack)
    switch = get_or_create(BasicNetworkSwitch, switch)
    pwr = get_or_create(PowerTowerXM, '%s-pwr1' % rack.name)
    ts = get_or_create(OpenGearCM4148, '%s-ts1' % rack.name)

    if not rack in dc:
        dc.insert(rack)
    if not switch in rack:
        rack.insert(switch, 31)
    if not pwr in rack:
        rack.insert(pwr, (28, 29))
    if not ts in rack:
        rack.insert(ts, 30)

    if switch.portFree('pwr-nema-5', 0):
        switch.connectPorts('pwr-nema-5', 0, pwr, '.aa8')
    if ts.portFree('pwr-nema-5', 0):
        ts.connectPorts('pwr-nema-5', 0, pwr, '.ab8')

    return (dc, rack, switch, pwr, ts)

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

    dc, rack, switch, pwr, ts = get_environment(dc_name, rack_name, switch_name)

    # Find the server's hostname and query clusto for it. If the server does not
    # exist, create it. Returns None if something went wrong.
    server = get_server(ipaddr)

    if not server:
        return

    pprint(server)

    if server.driver == 'basicvirtualserver':
        if not server.hasAttr('switchport'):
            server.addAttr('switchport', '%s,%s' % (rack.name, portnum))
            clusto.commit()
        return

    if portnum < 21:
        ifnum = 0
    else:
        ifnum = 1

    if not server.portFree('nic-eth', ifnum):
        if not server.getConnected('nic-eth', ifnum) == switch:
            server.disconnectPort('nic-eth', ifnum)
            server.connectPorts('nic-eth', ifnum, switch, portnum)
    else:
        server.connectPorts('nic-eth', ifnum, switch, portnum)

    if not server in rack:
        rack.insert(server, SWITCHPORT_TO_RU[portnum])

    ru = rack.getRackAndU(server)['RU'][0]
    if server.portFree('pwr-nema-5', 0):
        server.connectPorts('pwr-nema-5', 0, pwr, RU_TO_PWRPORT[ru])
    if server.portFree('console-serial', 0):
        server.connectPorts('console-serial', 0, ts, RU_TO_SWITCHPORT[ru])

    ifaces = discover_interfaces(ipaddr)
    for name in ifaces:
        if name == 'lo':
            continue
        n = ifaces[name]
        if not 'inet addr' in n:
            continue

        match = re.match('(?P<porttype>[a-z]+)(?P<num>[0-9]*)', name)
        if not match:
            print 'Unable to comprehend port name: %s' % name
            continue

        match = match.groupdict()
        if not match['num']:
            num = 0
        else:
            num = int(match['num'])
        porttype = match['porttype']

        #subnet.allocate(server, n['inet addr'])
        subnet = IPManager.getIPManager(n['inet addr'])
        if not server in subnet.owners(n['inet addr']):
            server.bindIPtoPort(n['inet addr'], 'nic-%s' % porttype, num)
        server.setPortAttr('nic-%s' % porttype, num, 'mac-address', n['hwaddr'])

    if not 'uniqueid' in server.attrKeys():
        for key, value in get_facts(ipaddr):
            if key == 'fqdn': continue
            server.addAttr(key, value)

    clusto.commit()

def bind_vservers():
    for vserver in clusto.getEntities(clustodrivers=(BasicVirtualServer,)):
        switchport = vserver.attrs('switchport')
        if not switchport: continue
        print 'Binding', repr(vserver)
        switchport = switchport[0]
        rack_name, portnum = switchport.value.rsplit(',', 1)
        portnum = int(portnum)
        rack = clusto.getByName(rack_name)
        switch = clusto.getByName(rack_name + '-sw1')
        print repr(switch)
        for device in rack.contents():
            if device.driver == 'basicserver':
                server = device
                conn = server.portInfo['nic-eth'][0]
                if conn['connection'] == switch and conn['otherportnum'] == portnum:
                    if not vserver in server:
                        server.insert(vserver)
                    print 'Bound %s to %s' % (vserver.name, server.name)

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
    bind_vservers()
    #pprint(clusto.getEntities())

if __name__ == '__main__':
    config = getClustoConfig()
    clusto.connect(config.get('clusto', 'dsn'))
    clusto.initclusto()
    main()
