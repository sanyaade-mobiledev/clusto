#!/usr/bin/env python
# -*- mode: python; sh-basic-offset: 4; indent-tabs-mode: nil; coding: utf-8 -*-
# vim: tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8
#
# Base script helper
# Copyright 2011, Jorge A Gallegos <kad@blegh.net>

import ConfigParser
import logging
import os
import sys

import clusto


levels = {
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG,
    'ERROR': logging.ERROR,
    'FATAL': logging.FATAL,
    'WARN': logging.WARN,
}


class CmdLineError(Exception):
    pass


class Script(object):

    logger = None
    config = None

    def __init__(self):
        pass

    def _get_description(self):
        if self.__class__.__doc__:
            help_string = self.__class__.__doc__
        else:
            help_string = '%s command help' % self.__class__.__name__.capitalize()
        return help_string

    def _setup_subparser(self, subparsers):
        parser = subparsers.add_parser(self.__class__.__name__.lower(),
            help=self._get_description())
        return parser

    def set_logger(self, logger):
        self.logger = logger

    def log(self, msg, level=logging.INFO):
        self.logger.log(level=level, msg=msg)

    def error(self, msg):
        self.log(msg, level=logging.ERROR)

    def warn(self, msg):
        self.log(msg, level=logging.WARN)

    def fatal(self, msg):
        self.log(msg, level=logging.FATAL)

    def debug(self, msg):
        self.log(msg, level=logging.DEBUG)

    def info(self, msg):
        self.log(msg)

    def run(self, *args, **kwargs):
        raise NotImplementedError()

    def load_config(self, filename):
        '''Find, parse, and return the configuration data needed by clusto.'''

        filename = filename or os.environ.get('CLUSTOCONFIG')

        if filename:
            if not os.path.exists(os.path.realpath(filename)):
                msg = "Config file %s doesn't exist." % filename
                self.error(msg)
                raise CmdLineError(msg)
        else:
            msg = "Config file %s doesn't exist." % filename
            self.error(msg)
            raise CmdLineError(msg)
            
        self.config = ConfigParser.SafeConfigParser()
        self.debug('Reading %s' % filename)
        self.config.read([filename])

        if not self.config.has_section('clusto'):
            self.config.add_section('clusto')

        if 'CLUSTODSN' in os.environ:
            self.config.set('clusto', 'dsn', os.environ['CLUSTODSN'])

        if not self.config.has_option('clusto', 'dsn'):
            raise CmdLineError("No database given for clusto data.")

    def get_config(self):
        '''Returns the config object'''

        return self.config

    def init_script(self, config, logger=None, initializedb=False):
        '''Initialize the clusto environment for clusto scripts.

        Connects to the clusto database, returns a python SafeConfigParser and a
        logger.

        '''

        if logger:
            self.set_logger(logger)
        self.load_config(config)
        clusto.connect(self.config)

        if initializedb:
            clusto.init_clusto()
        
        return self.config

def demodule(module):
    klass = ''.join([_.capitalize() for _ in module.split('_')])
    module = __import__('clusto.commands.%s' % module, fromlist=['clusto.commands'])
    klass = getattr(module, klass)
    return klass

def setup_parser(add_help=False):
    import argparse
    parser = argparse.ArgumentParser(prog=os.path.basename(sys.argv[0]),
        description='Clusto script', conflict_handler='resolve',
        add_help=add_help)
    parser.add_argument('--config', default='/etc/clusto/clusto.conf',
        help='Config file (defaults to /etc/clusto/clusto.conf)')
    parser.add_argument('--loglevel', default='INFO',
        help='Sets the logging level (defaults to INFO)')
    parser.add_argument('--dsn', help='Alternate DSN to use')
    return parser

def get_logger(loglevel='INFO'):
    format='%(name)s: %(levelname)-8s %(message)s'
    logging.basicConfig(format=format)
    log = logging.getLogger('clusto')
    log.setLevel(levels[loglevel])
    return log

def main():
    # These modules should only be imported if called from the cli
    from clusto import commands

    parser = setup_parser(add_help=True)
    subparsers = parser.add_subparsers(title='Available clusto commands', dest='subparser_name')
    for module in commands.__all__:
        try:
            klass = demodule(module)
            klass = klass()
            klass._setup_subparser(subparsers)
            klass = None
        except:
            pass
    args = parser.parse_args()

    log = get_logger(args.loglevel)
    if len(sys.argv) < 2:
        parser.print_help()
        return 0
    log.debug('Loading from clusto frontend: %s' % args.subparser_name)
    klass = demodule(args.subparser_name)
    klass = klass()
    klass.set_logger(log)
    try:
        klass.init_script(config=args.config, logger=log)
        klass.run(args)
    except Exception as e:
        log.error(str(e))


if __name__ == '__main__':
    sys.exit(main())

