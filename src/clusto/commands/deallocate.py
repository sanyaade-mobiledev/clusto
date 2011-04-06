#!/usr/bin/env python
# -*- mode: python; sh-basic-offset: 4; indent-tabs-mode: nil; coding: utf-8 -*-
# vim: tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8

import argparse
import sys

import clusto
from clusto import drivers
from clusto import script_helper


class Deallocate(script_helper.Script):
    '''
    This is a script that will deallocate machines from pool. That is, it will
    cleanup most attributes (except for system attributes) and will remove it
    from every pool it is on to then put it in a pre-defined 'unallocated' pool
    '''

    keep_attrs = ['port-console-serial', 'port-nic-eth', 'ip', 'system',
        'port-pwr-nema-5', 'memory', 'disk', 'processor']
    hosts = []

    def __init__(self):
        script_helper.Script.__init__(self)

    def _add_arguments(self, parser):
        parser.add_argument('--pool',
            help='Target pool after deallocation (you can set this in clusto.conf too '
                 'in deallocate.pool: --pool > clusto.conf:deallocate.pool > "unallocated")')
        parser.add_argument('--keep-attrs',
            help='Comma-separated keys to keep additional to whatever is configured '
                 'in clusto.conf in deallocate.keep_attrs')
        parser.add_argument('--reboot', action='store_true', default=False,
            help='Reboot the server after deallocating (defaults to False)')
        parser.add_argument('--shutdown', action='store_true', default=False,
            help='Power-off the server after deallocating (defaults to False)')
        parser.add_argument('--force-yes', action='store_true',
            default=False, help='Force yes to deallocate')
        parser.add_argument('objects', nargs='+',
            help='Server names or IP addresses')

    def add_subparser(self, subparsers):
        parser = self._setup_subparser(subparsers)
        self._add_arguments(parser)

    def _clean_attrs(self, host):
        '''
        Cleans the attributes from a given host, except for
        those in the "to keep" list
        '''
#   Clean attributes
        self.info('Cleaning up attributes from "%s"' % host.name)
        attrs = set(sorted([x.key for x in host.attrs() if x.key not in self.keep_attrs]))
        self.debug("List of attrs to remove: %s" % attrs)
        for attr in attrs:
            host.del_attrs(key=attr)

    def _deallocate(self, host):
        '''
        Remove the given host from all the parent pools
        '''
        self.info('Deallocating %s...' % host.name)
        pools = host.parents(clusto_types=[drivers.pool.Pool])
#   Remove from pools
        for pool in pools:
            if pool.name != 'fai' and pool.name != 'unallocated':
                self.info('Removing "%s" from pool "%s"' % (host.name, pool.name))
                pool.remove(host)

    def run(self, args):
#       get the 'unallocated' pool
        if args.pool:
            self.debug('Grabbing pool from parameter')
            pool = args.pool
        else:
            self.debug('Grabbing pool from config file or default')
            pool = self.get_conf('deallocate.pool', 'unallocated')
        self.debug('Unallocated pool is "%s"' % pool)

#       Load the attributes from the conf file
        for attr in self.get_conf('deallocate.keep_attrs', '').split(','):
            if attr.split():
                self.keep_attrs.append(attr.strip())
#       Append attributes from the command line, if any
        if args.keep_attrs:
            for attr in args.keep_attrs.split(','):
                if attr not in self.keep_attrs:
                    self.keep_attrs.append(attr)
        self.debug('Final list of attrs to keep: %s' % self.keep_attrs)
        for obj in args.objects:
            obj = clusto.get(obj)
            if obj not in self.hosts:
                self.hosts.extend(obj)
        self.info('This is the list of servers/ipaddresses that you will deallocate')
        for host in self.hosts:
            if host.get_ips():
                print '%s >> %s' % (host.name, ' '.join(host.get_ips()))
            else:
                print host.name

#       Ask for confirmation
        if not args.force_yes:
            sys.stdout.write('Are you absolutely sure you want to continue %s (yes/No)? ')
            sys.stdout.flush()

            try:
                line = sys.stdin.readline().strip()
            except KeyboardInterrupt:
                line = False

            if line != 'yes':
                print 'Aborting'
                return 7

        for host in self.hosts:
            if not isinstance(host, drivers.servers.BasicServer):
                self.warn('Cannot deallocate "%s" because is not a server' % host.name)
                continue
            self._deallocate(host)
            self._clean_attrs(host)
            if host not in pool:
                pool.insert(host)
            if args.reboot:
                host.power_reboot(captcha=False)
                continue
            if args.shutdown:
                host.power_off(captcha=False)
                continue
        self.info('Done.')

def main():
    deallocate, args = script_helper.init_arguments(Deallocate)
    return(deallocate.run(args))

if __name__ == '__main__':
    sys.exit(main())

