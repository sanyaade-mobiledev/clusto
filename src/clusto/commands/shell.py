#!/usr/bin/env python
# -*- mode: python; sh-basic-offset: 4; indent-tabs-mode: nil; coding: utf-8 -*-
# vim: tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8
#
# Shell command
# Copyright 2009, Ron Gorodetzky <ron@fflick.com>

import argparse
from IPython.Shell import IPShellEmbed
import sys

import clusto
from clusto import script
from clusto import *


class Shell(script.Script):
    '''
    This is an interactive clusto shell.

    Use at your own risk
    '''

    def __init__(self):
        script.Script.__init__(self)

    def run(self, args):
        opts = ['-prompt_in1', 'clusto [\#]> ', '-prompt_out', 'out [\#]> ']
        if args.loglevel == 'DEBUG':
            opts.append('-debug')
        ipshell = IPShellEmbed(opts, banner='\nThis is the clusto shell. Respect it.')
        ipshell()

def main():
    s = Shell()
    parent_parser = script.setup_parser()
    this_parser = argparse.ArgumentParser(parents=[parent_parser],
        description=s._get_description())
    args = this_parser.parse_args()
    s.init_script(args=args, logger=script.get_logger(args.loglevel))
    return(s.run(args))

if __name__ == '__main__':
    sys.exit(main())

