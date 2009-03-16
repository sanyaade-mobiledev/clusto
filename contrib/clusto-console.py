#!/usr/bin/env python
from clusto.scripthelpers import getClustoConfig
from clusto.drivers import IPManager
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

    ip = IPManager.getIP(server.name)
    if len(ip) == 0:
        print 'Unable to determine IP address for', server.name
        return
    ip = ip[0]

    if server.driver == 'basicserver':
        print 'Escape character is ~.'
        port = server.portInfo['console-serial'][0]
        tsport = port['otherportnum']
        tsname = port['connection'].connect('console-serial', tsport, 'digg')
        return

    if server.driver == 'basicvirtualserver':
        proc = Popen(SSH_CMD + ['-l', 'root', ip, 'xm list'], stdout=PIPE, stderr=STDOUT)
        stdout = proc.stdout.read()
        domu = None
        for line in stdout.split('\n')[1:]:
            line = line.strip('\r\n ')
            line = [x for x in line.split(' ') if x]
            if line[0].find(server.name) != -1:
                domu = line[0]
                break
        if not domu:
            print 'Unable to find a running domU containing the name', server.name
            return

        print 'Escape character is ^]'
        proc = Popen(SSH_CMD + ['-l', 'root', ip, 'xm console', domu])
        proc.communicate()
        return

    print '%s is not a server!' % sys.argv[1]

if __name__ == '__main__':
    config = getClustoConfig()
    clusto.connect(config.get('clusto', 'dsn'))
    #clusto.initclusto()
    main()
