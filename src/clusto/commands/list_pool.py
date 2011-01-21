#!/usr/bin/env python
# -*- mode: python; sh-basic-offset: 4; indent-tabs-mode: nil; coding: utf-8 -*-
# vim: tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8

import argparse
import sys

import clusto
from clusto import drivers
from clusto import script_helper


class ListPool(script_helper.Script):
    '''
    Lists servers that are part of two given pools.
    '''

    def __init__(self):
        script_helper.Script.__init__(self)

    def _add_arguments(self, parser):
        parser.add_argument('--names', default=False, action='store_true',
            help='Print names instead of ip addresses (defaults to False)')
        parser.add_argument('--recursive', default=False, action='store_true',
            help='Search resursively on both pools (defaults to False)')
        parser.add_argument('pool', nargs=2, metavar='pool',
            help='Pools to query (required)')

    def add_subparser(self, subparsers):
        parser = self._setup_subparser(subparsers)
        self._add_arguments(parser)

    def run(self, args):
        self.debug('Querying for pools %s' % args.pool)
        self.debug('Recursive search = %s' % args.recursive)
        serverset = clusto.get_from_pools(args.pool,
            clusto_types=[drivers.servers.BasicServer],
            search_children=args.recursive)
        for server in serverset:
            if args.names:
                print server.name
            else:
                try:
                    ip = server.get_ips()
                except Exception, e:
                    self.debug(e)
                    ip = None
                if ip:
                    print ip[0]
                else:
                    print server.name


def main():
    lp = ListPool()
    parent_parser = script_helper.setup_base_parser()
    this_parser = argparse.ArgumentParser(parents=[parent_parser],
        description=lp._get_description())
    lp._add_arguments(this_parser)
    args = this_parser.parse_args()
    lp.init_script(args=args, logger=script_helper.get_logger(args.loglevel))
    return(lp.run(args))

if __name__ == '__main__':
    sys.exit(main())

