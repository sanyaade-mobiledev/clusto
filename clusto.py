#!/usr/bin/env python

import sys
import os

from optparse import OptionParser

import clusto

from clusto.scripthelpers import *


def main(args):

    parser = OptionParser(usage="%prog [options] <command> [command args]")

    parser.add_option("-f", "--file", action="store",
                      type="string", dest="configfile")
    parser.add_option("--dsn", action="store",
                      type="string", dest="dsn")

    parser.disable_interspersed_args()
    (options, argv) = parser.parse_args(args[1:])


    config = setupClustoEnv(options)
    
    try:
        if len(argv) == 0 or argv[0] == 'help':
            print parser.get_usage()
            command = clusto.scripthelpers.getCommand('help')
        else:
            command = clusto.scripthelpers.getCommand(argv[0])
            if not command:
                raise CommandError("Command %s doesn't exist." % (argv[0]))

        return runcmd(command, argv[1:])
        
    except CommandError, msg:
        print msg
        print parser.get_usage()
        return runcmd(clusto.scripthelpers.getCommand('help'))


if __name__ == '__main__':
    sys.exit(main(sys.argv))
        
