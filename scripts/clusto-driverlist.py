#!/usr/bin/env python
"""
Print the available drivers for clusto
"""


import sys
import clusto

from optparse import OptionParser


def main(argv):

    parser = OptionParser(usage="usage: %prog [options] <driver> <name>")
    parser.add_option("--help-description", action="store_true",
                      dest="helpdesc",
                      help="print out the help description")

    (options, argv) = parser.parse_args(argv)

    if options.helpdesc:
        print ""
        return 0

    for i in sorted(clusto.driverlist):
        if clusto.driverlist[i].connector:
            continue
        if clusto.driverlist[i].__doc__:
            print '%s - %s' % (i, clusto.driverlist[i].__doc__.strip())
        else:
            print i

        
if __name__ == "__main__":
    sys.exit(main(sys.argv))
