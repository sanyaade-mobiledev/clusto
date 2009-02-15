from clusto.drivers import BasicDatacenter, BasicRack, BasicServer, BasicNetworkSwitch, PowerTowerXM
from clusto.scripthelpers import getClustoConfig
import clusto

from pprint import pprint
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

def import_ipmac(name, macaddr, ipaddr, portnum):
    '''
    Insert or update a server in clusto
    '''

    # Query clusto for a device matching the mac address.

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

    try:
        hostname = socket.gethostbyaddr(ipaddr)[0]
    except socket.herror:
        print 'Unable to find a hostname. You must add this server manually: %s' % ' '.join(name, macaddr, ipaddr, portnum)
        return

    server = get_or_create(BasicServer, hostname)
    if not server in rack:
        rack.insert(server, SWITCHPORT_TO_RU[portnum])

    if portnum < 21:
        ifnum = 0
    else:
        ifnum = 1

    server.setPortAttr('MACAddress', macaddr, 'nic-eth', ifnum)
    # TODO: Add the ip address to the server/port

    if not server.portFree('nic-eth', ifnum):
        if not server.getConnected('nic-eth', ifnum) == switch:
            server.disconnectPort('nic-eth', ifnum)
            server.connectPorts('nic-eth', ifnum, switch, portnum)
    else:
        server.connectPorts('nic-eth', ifnum, switch, portnum)

    if server.portFree('pwr-nema-5', 0):
        ru = rack.getRackAndU(server)['RU'][0]
        server.connectPorts('pwr-nema-5', 0, pwr, RU_TO_PWRPORT[ru])

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
        import_ipmac(switch, macaddr, ipaddr, port)
    #pprint(clusto.getEntities())

if __name__ == '__main__':
    config = getClustoConfig()
    print config.get('clusto', 'dsn')
    clusto.connect(config.get('clusto', 'dsn'))
    #clusto.initclusto()
    main()
