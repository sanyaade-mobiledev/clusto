#!/usr/bin/env python
# -*- mode: python; sh-basic-offset: 4; indent-tabs-mode: nil; coding: utf-8 -*-
# vim: tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8

import argparse
import sys

import clusto
from clusto import drivers
from clusto import script_helper


class Pool(script_helper.Script):
    '''
    Operate on a pool or on its objects. You can create, delete or show
    a pool and you can insert or remove items to/from a pool
    '''

    def __init__(self):
        script_helper.Script.__init__(self)

    def _get_pool(self, pool):
        p = clusto.get_by_name(pool)
        self.debug('%s is %s' % (pool, p))
        if not p or not isinstance(p, clusto.drivers.pool.Pool):
            self.error('The pool "%s" does not exist or is not a pool')
            return False
        return p

    def run_show(self, args):
        '''
        Prints the pool contents to stdout
        '''

        p = self._get_pool(args.pool[0])
        if not p:
            return -1
        print 'Printing the contents of pool %s' % p.name
        for item in p.contents():
            print '%s (%s)' % (item.name, item.type)

    def run_create(self, args):
        '''
        Creates a new, empty pool
        '''

        try:
            p = drivers.Pool(args.pool[0])
            return 0
        except Exception, e:
            self.warn(e)
            return 2

    def run_delete(self, args):
        '''
        Deletes a pool
        '''

        p = self._get_pool(args.pool[0])
        if not p:
            return -1
        sys.stdout.write('Are you sure you want to delete the pool %s (yes/NO)? ' % p.name)
        answer = sys.stdin.readline()
        if answer.strip() == 'yes':
            try:
                clusto.delete_entity(p.entity)
                return 0
            except Exception, e:
                self.error(e)
                return 3
        else:
            sys.stderr.write('Aborted\n')
            return 0

    def run_insert(self, args):
        '''
        Insert objects to a given pool
        '''

        if not args.objects:
            self.error('Please provide objects to insert to the pool')
            return -2
        p = self._get_pool(args.pool[0])
        if not p:
            return -1
        for obj in args.objects:
            try:
                obj = clusto.get_by_name(obj)
                self.debug(obj)
            except LookupError:
                self.warn('%s does not exist' % obj)
                continue
            if obj in p.contents():
                self.warn('%s is already in %s' % (obj.name, p.name))
                continue
            p.insert(obj)
        return 0

    def run_remove(self, args):
        '''
        Removes objects from a given pool
        '''

        if not args.objects:
            self.error('Please provide objects to remove from the pool')
            return -2
        p = self._get_pool(args.pool[0])
        if not p:
            return -1
        for obj in args.objects:
            try:
                obj = clusto.get_by_name(obj)
                self.debug(obj)
            except LookupError:
                self.warn('%s does not exist' % obj)
                continue
            if obj not in p.contents():
                self.warn('%s is not in %s' % (obj.name, p.name))
                continue
            p.remove(obj)
        return 0

    def run(self, args):
        getattr(self, 'run_%s' % args.action[0])(args)

    def _add_arguments(self, parser):
        parser.add_argument('action', nargs=1, metavar='action',
            choices=['show', 'create', 'delete', 'insert', 'remove'],
            help='Action to execute (show, create, delete, insert, remove)')
        parser.add_argument('pool', nargs=1, metavar='pool',
            help='Pool to modify (required)')
        parser.add_argument('objects', nargs='*',
            help='Objects to insert/remove (required if action = insert/remove)')

    def add_subparser(self, subparsers):
        parser = self._setup_subparser(subparsers)
        self._add_arguments(parser)


def main():
    pool, args = script_helper.init_arguments(Pool)
    return(pool.run(args))

if __name__ == '__main__':
    sys.exit(main())

