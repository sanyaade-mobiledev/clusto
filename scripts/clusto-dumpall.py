#!/usr/bin/env python
"""
Dump all the data in the clusto db in dot rc format
"""

import os
import sys
import logging

import clusto
from clusto.scripthelpers import *
from sqlalchemy.exceptions import SQLError

usage = os.path.split(sys.argv[0])[-1] + '<thingname> <key> <value>'

def parseargs(args):

    if len(args) != 0:
        raise CmdLineError("Wrong number of arguments.")
    
    return 0

def main(argv, config=None):

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
        

