#!/usr/bin/env python
"""
Print the available drivers for clusto
"""


import sys
import clusto


def main(argv):

    for i in sorted(clusto.driverlist):
        if clusto.driverlist[i].connector:
            continue
        if clusto.driverlist[i].__doc__:
            print '%s - %s' % (i, clusto.driverlist[i].__doc__.strip())
        else:
            print i

        
if __name__ == "__main__":
    sys.exit(main(sys.argv))
