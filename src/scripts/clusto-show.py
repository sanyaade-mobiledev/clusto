#!/usr/bin/env python
"""
Add a thing into clusto

"""

import os
import sys
import logging

import clusto
from clusto.scripthelpers import *
from sqlalchemy.exceptions import SQLError


class showthing(ClustoScript):

    usage = "%prog [options] <thingname>"

    short_description = "print out the data for a specific thing"

    option_list = []

    num_args = 1

    def main(self, argv, options, config, log):

        thingname = argv[1]

        thing = clusto.get_by_name(thingname)

        print thing

        return 0

if __name__ == '__main__':
    runscript(showthing)
        

