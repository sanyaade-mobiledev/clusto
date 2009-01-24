#!/usr/bin/env python
"""
Add a thing into clusto

./clusto-new.py <driver> <name> 
                                
"""

import os
import sys
import logging

from optparse import OptionParser

from clusto.scripthelpers import *
from sqlalchemy.exceptions import SQLError


class newthing(ClustoScript):
    short_description = "add a new thing to the clusto database"

    option_list = []

    num_args = 2
    
    def main(self, argv, options, config, log):

        drivername = argv[1]
        thingname = argv[2]
    
        try:
            driver = clusto.driverlist[drivername]
        except KeyError:
            raise CmdLineError("Driver %s doesn't exist." % (argv[0]))

        try:
            newthing = driver(thingname)
            clusto.flush()
        except SQLError, err:
            if 'not unique' in str(err):
                log.error('"%s" already exists.' % thingname)
                return 1


if __name__ == '__main__':
    runscript(newthing)
        


