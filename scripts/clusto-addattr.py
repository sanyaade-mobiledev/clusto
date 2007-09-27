#!/usr/bin/env python
"""
Add a thing into clusto

"""

import os
import sys
import logging

from optparse import OptionParser

import clusto
from clusto.scripthelpers import *
from sqlalchemy.exceptions import SQLError


def parseargs(args):

    if len(args) != 3:
        raise CmdLineError("Wrong number of arguments.")

    thingname = args[0]
    keyname = args[1]
    value = args[2]
    
    return thingname, keyname, value

def main(argv, config=None):

    parser = OptionParser(usage="usage: %prog [options] <thingname> <key> <value>")

    parser.add_option("-r", "--replace", action="store_true",
                      dest="replace",
                      help="replace all keys with the given key")

    
    (options, args) = parser.parse_args(argv)

    config, log = clusto.scripthelpers.initScript()
    
    try: 
        thingname, keyname, value = parseargs(args[1:])

        thing = clusto.getByName(thingname)

        if options.replace:
            thing.delAttrs(keyname)
            
        thing.addAttr(keyname, value)
        clusto.flush()

    except (CmdLineError, LookupError), msg:
        print msg
        print parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
        

