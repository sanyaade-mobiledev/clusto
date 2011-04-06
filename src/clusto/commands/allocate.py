#!/usr/bin/env python
# -*- mode: python; sh-basic-offset: 4; indent-tabs-mode: nil; coding: utf-8 -*-
# vim: tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8

import argparse
import operator
import random
import sys

import clusto
from clusto import drivers
from clusto import script_helper


class Allocate(script_helper.Script):
    '''
    Allocate servers from a given pool, you can specify filters
    to get a server with certain features. By default the script
    will search for the cheapest machine it can find
    '''

    def __init__(self):
        script_helper.Script.__init__(self)

    def _add_arguments(self, parser):
        parser.add_argument('--memory', '-m', type=int,
            help='Minimum system memory (in Gb)')
        parser.add_argument('--cores', '-c', type=int,
            help='Minimum number of system cores')
        parser.add_argument('--disk', '-d', type=int,
            help='Minimum disk size (in Gb)')
        parser.add_argument('--spindles', '-s', type=int,
            help='Minimum number of spindles')
        parser.add_argument('--to-pool', '-t', action='append', required=True,
            help='After allocating, add to the specified pools'
            ' (use more than once to set multi-pool)')
        parser.add_argument('--create-pools', '-C', action='store_true', default=False,
            help='Create the target pools if they do not exist')
        parser.add_argument('--from-pool', '-f',
            help='What pool to search in (you can set this in clusto.conf too '
                 'in allocate.pool: --from-pool > clusto.conf:allocate.pool > "unallocated")')
        parser.add_argument('--parent', '-p', required=True,
            help='Parent to start looking at. Can be a datacenter or a rack')
        parser.add_argument('number', nargs='?', type=int, default=1,
            help='How many machines to allocate, defaults to cheapest machine available')

    def add_subparser(self, subparsers):
        parser = self._setup_subparser(subparsers)
        self._add_arguments(parser)

    def __sort_servers(self, servers):
        tuples = []
        for server in servers:
            mem = server.attr_value(key='system', subkey='memory', default=None)
            cores = server.attr_value(key='system', subkey='cpucount',
                                      default=None)
            disk_size = server.attr_value(key='system', subkey='disk', default=None)
            disk_num = len(server.attrs(key='disk', subkey='size'))
            tuples.append((server, mem, cores, disk_size, disk_num))

        # do a single sort based on a four tuple as key!
        # tuple column order determines sort priority...
        tuples = sorted(tuples, key=lambda t:(t[3],t[2],t[1],t[4]))

        return [item[0] for item in tuples]

    def __make_filter(self, subkey, expected):
        def __filter(server):
            sys_info = server.attr_value(key='system', subkey=subkey, default=None)
            if not sys_info:
                return False
            if sys_info >= expected:
                return True
            else:
                return False
        
        def __filter_spindle(server):
            sys_len = len(server.attrs(key='disk', subkey='size'))
            return sys_len >= expected

        if subkey == 'spindles':
            return __filter_spindle
        else:
            return __filter

    def run(self, args):
        number = args.number

        if args.from_pool:
            self.debug('Grabbing pool from parameter')
            pool = args.from_pool
        else:
            self.debug('Grabbing pool from config file or default')
            pool = self.get_conf('allocate.pool', 'unallocated')
        self.debug('Unallocated pool is "%s"' % pool)

        pools = []
        try:
            if args.create_pools:
                pools = [ clusto.get_or_create(_, drivers.pool.Pool) for _ in args.pool ]
            else:
                pools = [ clusto.get_by_name(_, assert_driver=drivers.pool.Pool) for _ in args.to_pool ]
        except Exception as e:
            self.debug(e)
            self.error('There was an error when fetching/creating the pools to allocate the servers to')
            return 4
        self.debug('Target pool list: %s' % pools)

        try:
            pool = clusto.get_by_name(pool, assert_driver=drivers.pool.Pool)
        except Exception as e:
            self.debug(e)
            self.error('The pool "%s" does not exist' % pool)
            return 1

        try:
            parent = clusto.get(args.parent)
            if not parent:
                raise LookupError("Parent object is %s" % parent)
        except Exception as e:
            self.debug(e)
            self.error('The parent object "%s" does not exist' % args.parent)
            return 2
        parent = parent[0]
        if not isinstance(parent, drivers.racks.BasicRack) and not isinstance(parent, drivers.datacenters.BasicDatacenter):
            self.error('The parent "%s" is not a rack or a datacenter' % args.parent)
            return 2

        self.info('Searching for servers in "%s", this may take a while' % parent.name)

        unallocated = [ _ for _ in parent.contents(clusto_types=[drivers.servers.BasicServer], search_children=True) ]
        unallocated = [ _ for _ in unallocated if _ in pool and _.get_ips() ]
        self.debug('The unallocated list size is %d' % len(unallocated))
        if len(unallocated) < number:
            self.error('There are not enough servers in "%s" to fulfill your request' % args.parent)
            return 3

        filters = []
        if args.memory:
            filters.append(self.__make_filter('memory', args.memory * 1000))
        if args.disk:
            filters.append(self.__make_filter('disk', args.disk))
        if args.cores:
            filters.append(self.__make_filter('cpucount', args.cores))
        if args.spindles:
            filters.append(self.__make_filter('spindles', args.spindles))

        self.debug('Applying filters: %s' % filters)
        servers = []
        if not filters:
            servers = self.__sort_servers(unallocated)[:number]
        else:
            for func in filters:
                servers = filter(func, unallocated)[:number]
        self.debug('Server list: %s' % servers)

        for s in servers:
            pool.remove(s)
            for p in pools:
                p.insert(s)

        self.info('Allocated the following list of servers matching your filters '
            'were allocated from the pool "%s"' % pool.name)
        self.info('The servers were also added to the pools %s' % ','.join([ _.name for _ in pools ]))
        for s in servers:
            if s.get_ips():
                print s.get_ips()[0]
            else:
                print s.name

def main():
    allocate, args = script_helper.init_arguments(Allocate)
    return(allocate.run(args))


if __name__ == '__main__':
    sys.exit(main())

