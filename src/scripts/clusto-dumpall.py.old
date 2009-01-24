#!/usr/bin/env python
"""
Dump all the data in the clusto db in dot rc format
"""

import os
import sys
import logging

from optparse import OptionParser

import clusto

from clusto.scripthelpers import *
from sqlalchemy.exceptions import SQLError

usage = os.path.split(sys.argv[0])[-1] + '<thingname> <key> <value>'

def parseargs(args):

    if len(args) != 0:
        raise CmdLineError("Wrong number of arguments.")
    
    return 0

def main(argv, config=None):

    parser = OptionParser(usage="usage: %prog [options] <driver> <name>")
    parser.add_option("--help-description", action="store_true",
                      dest="helpdesc",
                      help="print out the help description")

    (options, argv) = parser.parse_args(argv)

    if options.helpdesc:
        print "create a new clusto thing"
        return 0

    config, log = clusto.scripthelpers.initScript()
    
    try:
        all = clusto.query()

        for i in all:
            print i

    except (CmdLineError, LookupError), msg:
        print msg
        print usage
        sys.exit(1)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
        

