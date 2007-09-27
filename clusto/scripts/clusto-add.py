#!/usr/bin/env python


import os
import sys

from optparse import OptionParser


def getCommand(command):
    """
    Return the path of the command passed in as an argument.
    """
    scriptbasename = "clusto-"
    scriptpaths = ["/etc/clusto/scripts",
                   "/usr/lib/clusto/scripts",
                   "/usr/local/lib/clusto/scripts",
                   ] + sys.path
    

    commandname = scriptbasename + command
    
    for path in scriptpaths:

        if os.path.exists(path):
            script = filter(lambda x: x == commandname,
                          os.listdir(path))
            if len(script) == 1:
                return os.path.join(path, script)

    return None
    
    
def runCommand(command, args):
    """
    Run the given command with the given args.
    """
    
    

def run(argv):

    parser = OptionParser()

    (options, args) = parser.parse_args()

    if not args:
        parser.error("You must supply a command.")

    command = args.pop()
    retval = runcommand(command, args)

    
    
