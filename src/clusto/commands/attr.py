#!/usr/bin/env python
# -*- mode: python; sh-basic-offset: 4; indent-tabs-mode: nil; coding: utf-8 -*-
# vim: tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8

import argparse
import sys

import clusto
from clusto import drivers
from clusto import script_helper
from pprint import pprint
import sys
import traceback


JSON=False
YAML=False
try:
    import yaml
    YAML=True
except ImportError:
    pass

try:
    import simplejson as json
    JSON=True
except ImportError:
    try:
        import json
        JSON=True
    except:
        pass


class Attr(script_helper.Script):
    '''
    Operate upon an object's attributes, you should be able to
    add, remove, list or set attributes of any kind
    '''

    obj = None
    format = 'list'

    def __init__(self):
        script_helper.Script.__init__(self)

    def run_show_yaml(self, attrs):
        self.debug('Printing in format: YAML')
        print yaml.safe_dump(attrs, encoding='utf-8',
            explicit_start=True, default_flow_style=False)
        return 0

    def run_show_json(self, attrs):
        self.debug('Printing in format: JSON')
        print json.dumps(attrs, sort_keys=True, indent=2)
        return 0

    def run_show_csv(self, attrs):
        self.debug('Printing in format: CSV')
        print 'key;subkey;number;"value"'
        for attr in attrs:
            print '%s;%s;%s;"%s"' % (
                str(attr['key'] or ''),
                str(attr['subkey'] or ''),
                str(int(attr['number'] or 0)),
                str(attr['value']))
        return 0

    def run_show_list(self, attrs):
        self.debug('Printing in format: List')
        maxkey = 3 + max([len(str(_['key'])) for _ in attrs] + [0])
        maxsubkey = 6 + max([len(str(_['subkey'])) for _ in attrs] + [0])
        maxnumber = 3 + max([len(str(_['number'])) for _ in attrs] + [0])

        if maxkey < 5: maxkey = 5
        if maxsubkey < 8: maxsubkey = 8

        print ''.join(['KEY'.ljust(maxkey, ' '), 'SUBKEY'.ljust(maxsubkey, ' '), 'VALUE'])
        for attr in attrs:
            print ''.join([str(_).ljust(maxsize, ' ') for _, maxsize in [
                (attr['key'], maxkey),
                (attr['subkey'], maxsubkey),
                (attr['value'], 0),
            ]])
        return 0

    def run_set(self, kwargs):
        kwargs.pop('merge_container_attrs')
        return self.obj.set_attr(**kwargs)

    def run_add(self, kwargs):
        kwargs.pop('merge_container_attrs')
        return self.obj.add_attr(**kwargs)

    def run_delete(self, kwargs):
        kwargs.pop('merge_container_attrs')
        return self.obj.del_attrs(**kwargs)

    def run_show(self, kwargs):
        attrs = self.obj.attrs(**kwargs)
        attrs.sort(key=lambda _: (_.key, _.number, _.subkey, _.value))
        result = []
        for attr in attrs:
            row = {
                'key': attr.key,
                'subkey': attr.subkey,
                'number': attr.number,
                'type': attr.datatype,
                'value': unicode(attr.value)
            }
            result.append(row)
        return (getattr(self, 'run_show_%s' % self.format)(result))

    def run(self, args):
        obj = clusto.get(args.obj[0])
        if not obj:
            self.error('Object %s does not exist' % args.obj[0])
            return -1
        self.obj = obj[0]
        opts = {}
        kwargs = dict(args.__dict__.items())
        self.format = args.format
        for k in ['key', 'subkey', 'value', 'merge_container_attrs']:
            if kwargs[k] != None:
                opts[k] = kwargs[k]
        return (getattr(self, 'run_%s' % args.action[0])(opts))

    def _add_arguments(self, parser):
        actions = ['add', 'show', 'set', 'delete']
        choices = ['list', 'csv']
        if JSON:
            choices.append('json')
        if YAML:
            choices.append('yaml')
        parser.add_argument('action', nargs=1, metavar='action', choices=actions,
            help='Action to execute (add, delete, set, show)')
        parser.add_argument('--format', choices=choices, default='list',
            help='What format to use to display the info, defaults to "list"')
        parser.add_argument('-k', '--key', help='Attribute key to filter on',
            default=None)
        parser.add_argument('-s', '--subkey', help='Attribute subkey to filter on',
            default=None)
        parser.add_argument('-v', '--value', help='Attribute value to filter on',
            default=None)
        parser.add_argument('-m', '--merge', default=False, action='store_true',
            dest='merge_container_attrs',
            help='Merge container attributes recursively (defaults to False)')
        parser.add_argument('obj', nargs=1, metavar='object',
            help='Object to modify/query attributes from')

    def add_subparser(self, subparsers):
        parser = self._setup_subparser(subparsers)
        self._add_arguments(parser)


def main():
    attr = Attr()
    parent_parser = script_helper.setup_base_parser()
    this_parser = argparse.ArgumentParser(parents=[parent_parser],
        description=attr._get_description())
    attr._add_arguments(this_parser)
    args = this_parser.parse_args()
    attr.init_script(args=args, logger=script_helper.get_logger(args.loglevel))
    return(attr.run(args))

if __name__ == '__main__':
    sys.exit(main())

