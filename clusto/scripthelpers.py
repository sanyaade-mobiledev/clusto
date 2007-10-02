
import os
import sys
import clusto
import logging
import commands

from ConfigParser import SafeConfigParser
from optparse import OptionParser, make_option


scriptpaths = [os.path.realpath(os.path.join(os.curdir, 'scripts')),
               '/etc/clusto/scripts',
               '/usr/local/bin',
               '/usr/bin',
               ] #+ filter(lambda x: not x.endswith('.egg'), sys.path)

def listClustoScripts(path):
    """
    Return a list of clusto scripts in the given path.
    """

    if not os.path.exists(path):
        return []

    if os.path.isdir(path):
        dirlist = os.listdir(path)
    else:
        dirlist = [path]

    available = filter(lambda x: x.startswith("clusto-")
                       and not x.endswith('~')
                       and os.access(os.path.join(path,x), os.X_OK),
                       dirlist)

    
    return map(lambda x: os.path.join(path, x), available)


def getCommand(cmdname):

    for path in scriptpaths:

        scripts = listClustoScripts(path)

        for s in scripts:
            if s.split('-')[1].split('.')[0] == cmdname:
                return s


    return None

def getCommandHelp(cmdname):

    fullpath = getCommand(cmdname)

    return commands.getoutput(fullpath + " --help-description")
    
def getClustoConfig(filename=None):
    """
    Find, parse, and return the configuration data needed by clusto.
    """

    filesearchpath = ['/etc/clusto/clusto.conf']

    if os.environ.has_key('CLUSTOCONFIG'):
        filename = os.environ['CLUSTOCONFIG']

    if not filename:
        filename = filesearchpath[0]

    if not os.path.exists(os.path.realpath(filename)):
        raise CmdLineError("no config file found.")
                           
    config = SafeConfigParser()

    config.read([filename])

    return config


def initScript():
    """
    Initialize the clusto environment for clusto scripts.
    """
    config = getClustoConfig(os.environ['CLUSTOCONFIG'])
    clusto.connect(os.environ['CLUSTODSN'])
    clusto.initclusto()
    
    logger = setupLogging(config)

    return (config, logger)


def runcmd(cmd, args=()):
    env = dict(os.environ)
    env['PYTHONPATH'] = ':'.join(sys.path)

    if not os.path.exists(cmd):
        raise CommandError("File Not Found.")
    if not os.access(cmd, os.X_OK):
        raise CommandError(cmd + " not Executable.")

    if cmd.endswith('.py'):
        pass
    args = [cmd] + list(args)

    return os.spawnve(os.P_WAIT, cmd, args, env)

    
def setupLogging(config=None):

    logging.basicConfig(level=logging.ERROR)

    return logging.getLogger()


def setupClustoEnv(options):
    """
    Take clusto parameters and put it into the shell environment.
    """


    if options.dsn:
        os.environ['CLUSTODSN'] = options.dsn
    if options.configfile:
        os.environ['CLUSTOCONFIG'] = options.configfile

    if os.environ.has_key('CLUSTOCONFIG'):
        config = getClustoConfig(os.environ['CLUSTOCONFIG'])
    else:
        config = getClustoConfig()

    if not os.environ.has_key('CLUSTODSN'):
        os.environ['CLUSTODSN'] = config.get('clusto','dsn')

    return config

class CmdLineError(Exception):
    pass

class CommandError(Exception):
    pass


class ClustoScript(object):

    usage = "%prog [options]"
    option_list = []
    num_args = None
    short_description = "sample short descripton"
    
    def __init__(self):
        self.parser = OptionParser(usage=self.usage,
                                   option_list=self.option_list)

        self.parser.add_option("--help-description",
                                action="callback",
                               callback=self._help_description,
                               dest="helpdesc",
                               help="print out the short command description")

        
    

    def _help_description(self, option, opt_str, value, parser, *args, **kwargs):

        print self.short_description
        sys.exit(0)
    


def runscript(scriptclass):

    script = scriptclass()

    (options, argv) = script.parser.parse_args(sys.argv)

    config, logger = initScript()

    try:
        if script.num_args != None and script.num_args != len(argv)-1:
            raise CmdLineError("Wrong number of arguments.")
        
        retval = script.main(argv,
                             options,
                             config=config,
                             log=logger)

    except (CmdLineError, LookupError), msg:
        print msg
        script.parser.print_help()
        return 1

    
    return sys.exit(retval)
