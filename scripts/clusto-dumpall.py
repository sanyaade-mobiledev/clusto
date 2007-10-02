#!/usr/bin/env python

from clusto.scripthelpers import *


class dumpall(ClustoScript):
    
    short_description = "dump the clusto db in dot-rc format"
    option_list = []

    def main(self, argv, options, config, log):

        all = clusto.query()

        for i in all:
            print i


if __name__ == '__main__':
    runscript(dumpall)
