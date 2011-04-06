#!/usr/bin/env python
# -*- mode: python; sh-basic-offset: 4; indent-tabs-mode: nil; coding: utf-8 -*-
# vim: tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8

import argparse
import sys
import yaml

import clusto
from clusto import drivers
from clusto import script_helper


class PuppetNode(script_helper.Script):
    '''
    This command will create a fully functional YAML dump that you can hook up to
    puppet to use as an external nodes artifact. The command will use every attribute
    from the container of the object to build a proper YAML with classes and attributes.
    '''

    def __init__(self):
        script_helper.Script.__init__(self)

    def _add_arguments(self, parser):
        parser.add_argument('--base', '-b',
            help='What should be the base class (if any) for this node, '
                 'you can also set this in clusto.conf '
                 'in puppet.base: --base-class> clusto.conf:puppet.base > "base::node")')
        parser.add_argument('--attribute', '-a',
            help='What is the attribute to filter for you can also set this in clusto.conf '
                 'in puppet.attribute: --attribute > clusto.conf:puppet.attribute > "puppet")')
        parser.add_argument('server', nargs=1,
            help='Server name or ipaddress')

    def add_subparser(self, subparsers):
        parser = self._setup_subparser(subparsers)
        self._add_arguments(parser)

    def run(self, args):
        server = args.server[0]
        try:
#           Lookup server name or ipaddress
            server = clusto.get(server)
            if not server:
#               Acount for fqdn
                server = clusto.get(server.split('.')[0])
                if not server:
                    raise LookupError('The object "%s" does not seem to exist' % args.server[0])
        except Exception as e:
            self.debug(e)
            self.error('"%s" does not exist' % args.server[0])
            return -1
        server = server[0]

        if args.attribute:
            self.debug('Grabbing attribute from parameter')
            attribute = args.attribute
        else:
            self.debug('Grabbing attribute from config file or default')
            attribute = self.get_conf('puppet.attribute', 'puppet')
        self.debug('Attribute is "%s"' % attribute)

        if args.base:
            self.debug('Grabbing base-class from parameter')
            base_class = args.base
        else:
            self.debug('Grabbing base-class from config file or default')
            base_class = self.get_conf('puppet.base', 'base::node')
        self.debug('Base class is "%s"' % base_class)

        result = {
            'classes': [base_class],
            'parameters': {},
        }

        for attr in server.attrs(key=attribute, merge_container_attrs=True):

            if attr.subkey == 'class':
                val = str(attr.value)
                if not val in result['classes']:
                    result['classes'].append(val)
                continue

            if attr.subkey == 'environment' and not 'environment' in result:
                result['environment'] = str(attr.value)
                continue

            if isinstance(attr.value, int):
                val = attr.value
            else:
                val = str(attr.value)

            subkey = str(attr.subkey)
            if not subkey in result['parameters']:
                result['parameters'][subkey] = val

#       Print the YAML object to stdout
        yaml.dump(result, sys.stdout, default_flow_style=False, explicit_start=True, indent=2)


def main():
    pn, args = script_helper.init_arguments(PuppetNode)
    return(pn.run(args))

if __name__ == '__main__':
    sys.exit(main())

