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

    if server.driver == 'basicserver':
        print 'Escape character is ~.'
        port = server.portInfo['console-serial'][0]
        tsport = port['otherportnum']
        tsname = port['connection'].connect('console-serial', tsport, 'digg')
        return

    if server.driver == 'basicvirtualserver':
        print 'Escape character is ^]'
        host = server.parents()[0].attrs('fqdn')[0].value
        proc = Popen(['ssh', '-l', 'root', host, 'xm console %s' % server.name])
        proc.communicate()
        return

    print '%s is not a server!' % sys.argv[1]

if __name__ == '__main__':
    config = getClustoConfig()
    clusto.connect(config.get('clusto', 'dsn'))
    #clusto.initclusto()
    main()
