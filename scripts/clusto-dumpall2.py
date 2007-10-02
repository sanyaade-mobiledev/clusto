#!/usr/bin/env python

from clusto.scripthelpers import *


class dumpall(ClustoScript):

    
    short_description = "an example script"
    option_list = []

    def main(self, argv, options, config, log):

        all = clusto.query()

        for i in all:
            print i


if __name__ == '__main__':
    runscript(dumpall)
