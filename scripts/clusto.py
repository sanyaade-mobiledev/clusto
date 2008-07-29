#!/usr/bin/env python

import sys
import os

import cmdln

import clusto

from clusto.scripthelpers import *


class ClustoCmd(cmdln.Cmdln):
    name = "clusto"

    withconfig = False

    def get_optparser(self):
        parser = cmdln.Cmdln.get_optparser(self)
        parser.set_defaults(clustodsn="sqlite:///:memory:",)
        return parser
            
    def postoptparse(self):
        cmdln.Cmdln.postoptparse(self)

        clusto.connect(self.options.clustodsn)
        clusto.initclusto()
        

    def do_driverlist(self, subcmd, opts):

        for driver in sorted(clusto.driverlist):
            print driver

    def do_typelist(self, subcmd, opts):

        for clustotype in sorted(clusto.typelist):
            print clustotype
            


if __name__ == '__main__':
    clustocmd = ClustoCmd()
    sys.exit(clustocmd.main())
        
