#!/usr/bin/env python

from clusto.scripthelpers import *


class Example(ClustoScript):

    short_description = "an example script"
    option_list = [
        make_option("-f", "--filename",
                    action="store", type="string", dest="filename"),
        make_option("-q", "--quiet",
                    action="store_false", dest="verbose"),
        ]


    def main(argv, options=None, config=None):

        if option.filename:
            print "the filename is %s" % (option.filename)

        print "this is the main function."
        

Example.runscript()
