#!/usr/bin/env python
# -*- mode: python; sh-basic-offset: 4; indent-tabs-mode: nil; coding: utf-8 -*-
# vim: tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8

import argparse
import sys

import clusto
from clusto import drivers
from clusto import script_helper


class Fai(script_helper.Script):
    '''
    This is a script that will perform an FAI process (Fully Automated Install)
    on a machine. It basically will put the target option in the appropriate
    pool and then reboot it.
    '''

    def __init__(self):
        script_helper.Script.__init__(self)

    def _add_arguments(self, parser):
        parser.add_argument('--pool',
            help='What pool to use for FAI (you can set this in clusto.conf too '
                 'in fai.pool: --pool > clusto.conf:fai.pool > "fai")')
        parser.add_argument('--no-reboot', action='store_true', default=False,
            help='Stop the script from rebooting, defaults to False (you can set '
                 'this in clusto.conf too in fai.reboot: --no-reboot > '
                 'clusto.conf:fai.reboot > False')
        parser.add_argument('--disk-class',
            help='FAI needs a disk class to partition properly, set one here if needed')
        parser.add_argument('object', nargs=1,
            help='Server name or IP address')

    def add_subparser(self, subparsers):
        parser = self._setup_subparser(subparsers)
        self._add_arguments(parser)

    def run(self, args):
        try:
            obj = clusto.get(args.object[0])
        except Exception as e:
            self.debug(e)
            self.error('"%s" does not exist' % args.object[0])
            return -1
        obj = obj[0]
        if not isinstance(obj, drivers.BasicServer):
            self.error('Seems like "%s" is not a server (type=%s), you cannot FAI this' % (obj.name, obj.type))
            return 1
        self.debug('Working with %s' % obj)
        if args.disk_class:
            obj.set_attr(key='fai', subkey='class', value=args.disk_class)
        disk_class = obj.attrs(key='fai', subkey='class', merge_container_attrs=True)
        if not disk_class:
            self.error('The server "%s" lacks fai class attribute, please '
                       'set one (hint: --disk-class at least)' % obj.name)
            return 2
        ip = obj.get_ips()
        if not ip:
            self.error('"%s" lacks an IP address, cannot FAI' % obj.name)
            return 3
        ip = ip[0]
        mac = obj.attrs(key='port-nic-eth', subkey='mac', number=1)
        if not mac:
            self.error('"%s" lacks a MAC Address, cannot FAI' % obj.name)
            return 4
        mac = mac[0].value

        if args.pool:
            self.debug('Grabbing pool from parameter')
            pool = args.pool
        else:
            self.debug('Grabbing pool from config file or default')
            pool = self.get_conf('fai.pool', 'fai')
        self.debug('FAI pool is "%s"' % pool)
        try:
            pool = clusto.get_by_name(pool)
        except Exception as e:
            self.debug(e)
            self.error('The pool "%s" does not exist' % pool)
            return 5
        if not isinstance(pool, drivers.Pool):
            self.error('Looks like "%s" is not a pool' % pool.name)
            return 6

        print 'IP: %s' % ip
        print 'MAC: %s' % mac
        print 'FAI classes: %s' % ' '.join([ _.value for _ in disk_class ])
        print 'Parents: %s' % ' '.join([ _.name for _ in obj.parents() ])

        sys.stdout.write('Are you absolutely sure you want to FAI %s (yes/No)? ' % obj.name)
        sys.stdout.flush()

        try:
            line = sys.stdin.readline().rstrip('\r\n')
        except KeyboardInterrupt:
            line = False

        if line != 'yes':
            print 'Aborting'
            return
        else:
            if obj not in pool:
                pool.insert(obj)
            if not args.no_reboot:
                obj.power_reboot(captcha=False)
                print '%s is rebooting now.' % obj.name
            print 'Done.'
        return


def main():
    fai, args = script_helper.init_arguments(Fai)
    return(fai.run(args))

if __name__ == '__main__':
    sys.exit(main())

