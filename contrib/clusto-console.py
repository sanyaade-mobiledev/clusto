#!/usr/bin/env python
from clusto.scripthelpers import getClustoConfig
import clusto

from subprocess import Popen
import sys

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

    port = server.portInfo['console-serial'][0]
    tsport = port['otherportnum'] + 3000
    tsname = port['connection'].name

    proc = Popen(['ssh', '-p', str(tsport), 'digg@%s' % tsname])
    proc.communicate()

if __name__ == '__main__':
    config = getClustoConfig()
    clusto.connect(config.get('clusto', 'dsn'))
    #clusto.initclusto()
    main()
