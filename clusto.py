#!/usr/bin/env python

import sys
import os

from optparse import OptionParser


import clusto

def usage():
    """
    The usage of this script.
    """

    return ' '.join([sys.argv[0],
                     "<command>",
                     "[command args]",
                     ])
                     

class CommandError(Exception):
    pass

def runcmd(cmd, args=()):
    env = dict(os.environ)
    env['PYTHONPATH'] = ':'.join(sys.path)

    if not os.path.exists(cmd):
        raise CommandError("File Not Found.")
    if not os.access(cmd, os.X_OK):
        raise CommandError(cmd + " not Executable.")

    args = [cmd] + list(args)

    return os.spawnve(os.P_WAIT, cmd, args, env)

    
def main(argv):

    try:
        if len(argv) <= 1:
            command = clusto.scripthelpers.getCommand('help')
        else:
            command = clusto.scripthelpers.getCommand(argv[1])
            if not command:
                raise CommandError("Command %s doesn't exist." % (argv[1]))

        runcmd(command)
    except CommandError, msg:
        print msg
        print usage()
        runcmd(clusto.scripthelpers.getCommand('help'))


if __name__ == '__main__':
    sys.exit(main(sys.argv))
        
