#!/usr/bin/env python
"""
Print the help for clusto
"""


import sys
import clusto.scripthelpers

import clusto
from clusto.scripthelpers import *

from optparse import OptionParser

def parseargs(args):

    pass

def main(argv):

    parser = OptionParser(usage="usage: %prog [options]")
    parser.add_option("--help-description", action="store_true",
                      dest="helpdesc",
                      help="print out the help description")
    (options, args) = parser.parse_args(argv)

    if options.helpdesc:
        print "print available clusto commands"
        return 0
    
    helpmsg = ["Available Commands:"]

    scripts = set()

    for i in clusto.scripthelpers.scriptpaths:
        scripts.update(map(lambda s: s.split('-')[1].split('.')[0],
                           clusto.scripthelpers.listClustoScripts(i)))


    helpmsg.extend(["%s - %s" % (i, clusto.scripthelpers.getCommandHelp(i))
                    for i in sorted(scripts)])

    print
    print '\n\t'.join(helpmsg)
    print
    
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
