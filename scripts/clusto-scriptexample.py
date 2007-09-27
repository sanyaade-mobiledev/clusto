#!/usr/bin/env python
"""
SOME DOCUMENTATION
"""

import os
import sys
import logging

from optparse import OptionParser

import clusto
from clusto.scripthelpers import *

def parseargs(args):

    pass

def main(argv, config=None):

    parser = OptionParser(usage="usage: %prog [options]")
    
    (options, args) = parser.parse_args(argv)

    config, log = clusto.scripthelpers.initScript()
    
    try: 
        ## do your work here
        pass
    except Exception, msg:
        print msg
        print parser.print_help()
        return 1

if __name__ == '__main__':
    sys.exit(main(sys.argv))
        

