#!/usr/bin/env python
"""
Add a thing into clusto

"""

import os
import sys
import logging

from optparse import OptionParser

import clusto
from clusto.scripthelpers import *
from sqlalchemy.exceptions import SQLError


class add_attr(ClustoScript):

    usage = "%prog [options] <thingname> <key> <value>"
    short_description = "add an attribute to a thing"

    option_list = [make_option("-r", "--replace", action="store_true",
                               dest="replace",
                               help="replace all keys with the given key")]

    num_args = 3

    def main(self, argv, options, config, log):

        thingname = argv[1]
        keyname = argv[2]
        value = argv[3]

    
        thing = clusto.get_by_name(thingname)

        if options.replace:
            thing.del_attrs(keyname)
            
        thing.add_attr(keyname, value)
        clusto.flush()

                    

if __name__ == '__main__':
    runscript(add_attr)
        

