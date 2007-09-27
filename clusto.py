#!/usr/bin/env python

import sys
import os

from optparse import OptionParser


import clusto

from clusto.scripthelpers import *

def usage():
    """
    The usage of this script.
    """

    return ' '.join([sys.argv[0],
                     "<command>",
                     "[command args]",
                     ])
                     


def runcmd(cmd, args=()):
    env = dict(os.environ)
    env['PYTHONPATH'] = ':'.join(sys.path)

    if not os.path.exists(cmd):
        raise CommandError("File Not Found.")
    if not os.access(cmd, os.X_OK):
        raise CommandError(cmd + " not Executable.")

    args = [cmd] + list(args)

    return os.spawnve(os.P_WAIT, cmd, args, env)

    
def main(args):

    parser = OptionParser()

    parser.add_option("-f", "--file", action="store",
                      type="string", dest="filename")
    parser.add_option("--dsn", action="store",
                      type="string", dest="dsn")
    parser.disable_interspersed_args()
    (options, argv) = parser.parse_args(args[1:])

    if options.filename:
        os.environ['CLUSTOCONF'] = os.path.realpath(options.filename)
        
    
    try:
        if len(argv) == 0:
            print usage()
            command = clusto.scripthelpers.getCommand('help')
        else:
            command = clusto.scripthelpers.getCommand(argv[0])
            if not command:
                raise CommandError("Command %s doesn't exist." % (argv[0]))

        return runcmd(command, argv[1:])
        
    except CommandError, msg:
        print msg
        print usage()
        return runcmd(clusto.scripthelpers.getCommand('help'))


if __name__ == '__main__':
    sys.exit(main(sys.argv))
        
