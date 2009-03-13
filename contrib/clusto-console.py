#!/usr/bin/env python
from clusto.scripthelpers import getClustoConfig
from clusto.drivers import BasicRack
import clusto

from subprocess import Popen
import sys

RU_TO_CONSOLEPORT = {1: 3001, 2: 3002, 3: 3003, 4: 3004, 5: 3005, 7: 3006, 8: 3007, 9: 3008, 10: 3009, 11: 3010, 13: 3011, 14: 3012, 15: 3013, 16: 3014, 17: 3015, 19: 3016, 20: 3017, 21: 3018, 22: 3019, 23: 3020}

def main():
    if len(sys.argv) < 2:
        print 'Usage: clusto console <name>'
        sys.exit(0)

    try:
        server = clusto.getByName(sys.argv[1])
    except LookupError:
        print '%s is not a clusto name' % sys.argv[1]
        return

    if server.type != 'server':
        print '%s is not a server!' % sys.argv[1]
        return

    rackandu = BasicRack.getRackAndU(server)
    ru = rackandu['RU'][0]
    rack = rackandu['rack']

    tsname = rack.name + '-ts1'
    proc = Popen(['ssh', '-p', str(RU_TO_CONSOLEPORT[ru]), 'digg@%s' % tsname])
    proc.communicate()

if __name__ == '__main__':
    config = getClustoConfig()
    clusto.connect(config.get('clusto', 'dsn'))
    #clusto.initclusto()
    main()
