#!/usr/bin/env python
# -*- mode: python; sh-basic-offset: 4; indent-tabs-mode: nil; coding: utf-8 -*-
# vim: tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8
#
# Base script helper
# Copyright 2011, Jorge A Gallegos <kad@blegh.net>

import argparse
import ConfigParser
import glob
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
    '''
    Base script helper class
    '''

    logger = None
    config = None

    def __init__(self):
        pass

    def _get_description(self):
        '''
        Returns the docstring for the class if there's one,
        otherwise it returns a generic blurb
        '''

        if self.__class__.__doc__:
            help_string = self.__class__.__doc__
        else:
            help_string = '%s command help' % self.__class__.__name__.capitalize()
        return help_string

    def _setup_subparser(self, subparsers):
        '''
        Sets up the command subparser, this should (in theory at least)
        only be called from within add_subparser()
        '''

        command_name = self.__module__.split('.')[-1].lower().replace('_', '-')
        parser = subparsers.add_parser(command_name, help=self._get_description())
        return parser

    def add_subparser(self, subparser):
        '''
        Adds the command subparser to the base parser. This method should
        always call _setup_subparser so the command becomes available in
        the argparse namespace, otherwise it won't be listed
        '''

        self._setup_subparser(subparser)

    def set_logger(self, logger):
        '''
        Sets the class logger to whatever logging facility we provide
        '''
        self.logger = logger

    def log(self, msg, level=logging.INFO):
        '''
        I dislike having to type self.logger.log()
        '''
        self.logger.log(level=level, msg=msg)

    def error(self, msg):
        '''
        Passthrough to self.logger.error()
        '''
        self.log(msg, level=logging.ERROR)

    def warn(self, msg):
        '''
        Passthrough to self.logger.warn()
        '''
        self.log(msg, level=logging.WARN)

    def fatal(self, msg):
        '''
        Passthrough to self.logger.fatal()
        '''
        self.log(msg, level=logging.FATAL)

    def debug(self, msg):
        '''
        Passthrough to self.logger.debug()
        '''
        self.log(msg, level=logging.DEBUG)

    def info(self, msg):
        '''
        Passthrough to self.logger.info()
        '''
        self.log(msg)

    def run(self, *args, **kwargs):
        '''
        Main command loop, should be implemented in child classes
        '''
        raise NotImplementedError()

    def get_conf(self, path, default=None):
        '''
        Returns the config value
        '''

        (section, option) = path.split('.')
        if self.config.has_option(section, option):
            return self.config.get(section, option)
        else:
            return default

    def _add_arguments(self, *args, **kwargs):
        pass

    def init_script(self, args, logger=None):
        '''
        Initialize the clusto environment for clusto scripts.

        Connects to the clusto database, returns a python SafeConfigParser
        '''

        if logger:
            self.set_logger(logger)
        if 'CLUSTOCONFIG' in os.environ:
            filename = os.environ['CLUSTOCONFIG']
        else:
            filename = args.config
        self.config = load_config(filename, args.dsn, logger)
        self.debug('Connecting to %s' % self.config.get('clusto', 'dsn'))
        clusto.connect(self.config)

        return self.config

def load_config(filename=None, dsn=None, logger=None):
    '''
    Find, parse, and return the configuration data needed by clusto
    '''

    if not logger:
        logger = get_logger()

    config = ConfigParser.SafeConfigParser()
    config.add_section('clusto')

    if filename is not None:
        if not os.path.exists(os.path.realpath(filename)):
            msg = "Config file %s doesn't exist." % filename
            logger.error(msg)
            raise CmdLineError(msg)
        
        logger.debug('Reading %s' % filename)
        config.read([filename])

        if not config.has_section('clusto'):
            config.add_section('clusto')

        if config.has_option('clusto', 'include'):
            for pattern in config.get('clusto', 'include').split():
                for filename in glob.glob(pattern):
                    fn = os.path.realpath(filename)
                    logger.debug('Trying to add config file: "%s"' % fn)
                    try:
                        config.read(fn)
                    except ConfigParser.ParsingError, cppe:
                        logger.warn(cppe)
                    except Exception, e:
                        logger.debug(e)

    if dsn:
        config.set('clusto', 'dsn', dsn)
    elif 'CLUSTODSN' in os.environ:
        config.set('clusto', 'dsn', os.environ['CLUSTODSN'])

    if not config.has_option('clusto', 'dsn'):
        raise CmdLineError("No database given for clusto data.")

    plugins = []
    if config.has_option('clusto', 'plugins'):
        plugins += clusto.get('clusto', 'plugins').split(',')
    if 'CLUSTOPLUGINS' in os.environ:
        plugins += os.environ['CLUSTOPLUGINS'].split(',')
    for plugin in plugins:
        logger.debug('Loading plugin %s' % plugin)
        module = __import__(plugin)

    return config

def demodule(module):
    '''
    Returns a class out of a given module name by doing:
    some_name_in_this_form => SomeNameInThisForm()
    '''

    klass = ''.join([_.capitalize() for _ in module.split('_')])
    module = __import__('clusto.commands.%s' % module, fromlist=['clusto.commands'])
    klass = getattr(module, klass)
    return klass

def setup_base_parser(add_help=False):
    '''
    Setups the base parser with common options, this is used here down below
    or can alternatively be used in the commands main() call for standalone
    script support
    '''

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

def get_logger(name='', loglevel='INFO'):
    '''
    Returns a basic std{out,err} logger
    '''

    format='%(name)s: %(levelname)-8s %(message)s'
    logging.basicConfig(format=format)
    log = logging.getLogger('command.%s' % name)
    log.setLevel(levels[loglevel])
    return log

def init_arguments(klass):
    obj = klass()
    parent_parser = setup_base_parser()
    this_parser = argparse.ArgumentParser(parents=[parent_parser],
        description=obj._get_description())
    obj._add_arguments(this_parser)
    args = this_parser.parse_args()
    log = get_logger(klass.__module__.split('.')[-1], args.loglevel)
    obj.init_script(args=args, logger=log)
    return obj, args

def main():
    # should only be imported if called from the cli
    from clusto import commands

    parser = setup_base_parser(add_help=True)
    subparsers = parser.add_subparsers(title='Available clusto commands', dest='subparser_name')
    help_subparser = subparsers.add_parser('help', help='Print clusto help')
    for dirpath, dirname, filenames in os.walk(commands.__path__[0]):
        for fn in filenames:
            if not fn.endswith('pyc') and not fn.startswith('__'):
                module = fn.split('.')[0]
                try:
                    klass = demodule(module)
                    klass = klass()
                    klass.add_subparser(subparsers)
                    klass = None
                except Exception, e:
                    pass
    args = parser.parse_args()

    log = get_logger(args.subparser_name, args.loglevel)
    if len(sys.argv) < 2:
        parser.print_help()
        return 0
    if args.subparser_name == 'help':
        parser.print_help()
        return 0
    log.debug('Loading from clusto frontend: %s' % args.subparser_name)
    klass = demodule(args.subparser_name.replace('-', '_'))
    klass = klass()
    klass.set_logger(log)
    try:
        klass.init_script(args=args, logger=log)
        return(klass.run(args))
    except Exception as e:
        log.error(str(e))
        return 99


if __name__ == '__main__':
    sys.exit(main())

