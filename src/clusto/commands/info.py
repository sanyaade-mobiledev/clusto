#!/usr/bin/env python
# -*- mode: python; sh-basic-offset: 4; indent-tabs-mode: nil; coding: utf-8 -*-
# vim: tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8

import argparse
import re
import sys

import clusto
from clusto.drivers import IPManager
from clusto import script_helper

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


class Info(script_helper.Script):
    '''
    This is a script that displays information about a certain object
    (or list of objects) and displays it to stdout.
    '''

    def __init__(self):
        script_helper.Script.__init__(self)

    def format_line(self, key, value, pad=20):
        if value:
            if isinstance(value, list):
                value = ', '.join(value)
            key += ':'
            print key.ljust(pad, ' '), value

    def print_summary(self, items):
        self.debug('Printing with format=summary')
        for item in items:
            self.format_line('Name', item.pop('name'))
            self.format_line('Type', item.pop('type'))
            if 'ip' in item.keys():
                self.format_line('IP', item.pop('ip'))
            self.format_line('Description', item.pop('description'))
            if 'parents' in item.keys():
                self.format_line('Parents', item.pop('parents'))
            if 'contents' in item.keys():
                self.format_line('Contents', item.pop('contents'))
            print '\n'
            keys = sorted(item.keys())
            for k in keys:
                self.format_line(k.capitalize(), item[k])
            print '-' * 80


    def print_oneline(self, items):
        self.debug('Printing with format=oneline')
        for item in items:
            line = '%s(%s);' % (item.pop('name'), item.pop('type'))
            line += '%s;' % (','.join([ '"%s"' % _ for _ in item.pop('description') ]))
            if 'ip' in item.keys():
                line += 'ip=%s;' % (','.join([ _ for _ in item.pop('ip') ]))
            if 'parents' in item.keys():
                line += 'parents=%s;' % (','.join([ _ for _ in item.pop('parents') ]))
            if 'contents' in item.keys():
                line += 'contents=%s;' % (','.join([ _ for _ in item.pop('contents') ]))
            keys = sorted(item.keys())
            for k in keys:
                line += '%s=%s;' % (k, item[k])
            print line

    def print_json(self, items):
        self.debug('Printing with format=json')
        print json.dumps(items, sort_keys=True, indent=2)

    def print_yaml(self, items):
        self.debug('Printing with format=yaml')
        print yaml.safe_dump(items, encoding='utf-8',
            explicit_start=True, default_flow_style=False)

    def run(self, args):
        if not args.items:
            print 'You need to provide at least one item. Use --help'
            return 0
        item_list = []
        self.debug('Fetching the list of items: %s' % ','.join(args.items))
        for item in args.items:
            obj = clusto.get(item)
            if not obj:
                self.warn("The item %s couldn't be found" % item)
                continue
            obj = obj[0]
            self.debug('Object found! %s' % obj)
            item_attrs = {
                'name': obj.name,
                'type': obj.type,
            }
#           Fetch system attrs
            for attr in obj.attrs(key='system'):
                item_attrs[attr.subkey] = attr.value
#           fetch description(s)
            values = obj.attrs(key='description')
            if values:
                item_attrs['description'] = [ _.value for _ in values]
            else:
                item_attrs['description'] = ''
#           fetch parent(s)
            values = obj.parents()
            if values:
                item_attrs['parents'] = [ _.name for _ in values ]
#           fetch content(s)
            values = obj.contents()
            if values:
                item_attrs['contents'] = [ _.name for _ in values ]
#           fetch ip(s)
            values = IPManager.get_ips(obj)
            if values:
                item_attrs['ip'] = [ _ for _ in values ]
#           fetch mac(s)
            values = [ _ for _ in obj.attrs(key='port-nic-eth') if _.subkey.find('mac') != -1 ]
            if values:
                for value in values:
                    item_attrs['mac%d' % value.number] = value.value
            item_list.append(item_attrs)
        getattr(self, 'print_%s' % args.format)(item_list)

    def _add_arguments(self, parser):
        choices = ['summary', 'oneline']
        if JSON:
            choices.append('json')
        if YAML:
            choices.append('yaml')
        parser.add_argument('--format', choices=choices, default='summary',
            help='What format to use to display the info, defaults to "summary"')
        parser.add_argument('items', nargs='*', metavar='item',
            help='List of one or more objects to show info')

    def add_subparser(self, subparsers):
        parser = self._setup_subparser(subparsers)
        self._add_arguments(parser)

def main():
    info, args = script_helper.init_arguments(Info)
    return(info.run(args))

if __name__ == '__main__':
    sys.exit(main())

