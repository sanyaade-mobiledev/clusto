#!/usr/bin/env python
"""
Print the available drivers for clusto
"""


import sys
import clusto

from clusto.scripthelpers import *
from optparse import make_option

class driverlist(ClustoScript):

    usage = "%prog"
    option_list = [make_option("-c", "--connectors",
                               help="also list connectors",
                               action="store_true",
                               dest="connectors")]
    num_args = 0

    short_description = "print out the list of available drivers"

    def main(self, argv, options, config, log):
        
        for i in sorted(clusto.driverlist):
            if clusto.driverlist[i].connector and not options.connectors:
                continue
            if clusto.driverlist[i].__doc__:
                print '%s - %s' % (i, clusto.driverlist[i].__doc__.strip())
            else:
                print i

        
if __name__ == "__main__":
    runscript(driverlist)
