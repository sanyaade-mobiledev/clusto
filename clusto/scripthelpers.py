
import os
import clusto
import logging

from ConfigParser import SafeConfigParser


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

def getClustoConfig(filename=None):
    """
    Find, parse, and return the configuration data needed by clusto.
    """

    filesearchpath = ['/etc/clusto/clusto.conf']

    if os.environ.has_key('CLUSTOCONF'):
        filename = os.environ['CLUSTOCONF']

    if not filename:
        filename = filesearchpath[0]

    if not os.path.exists(filename):
        raise CmdLineError("no config file found.")
                           
    config = SafeConfigParser()

    config.read([filename])

    return config


def initScript():
    config = getClustoConfig()

    clusto.connect(config.get('clusto', 'dsn'))
    clusto.initclusto()
    
    logger = setupLogging(config)

    return (config, logger)
    
def setupLogging(config=None):

    logging.basicConfig(level=logging.ERROR)

    return logging.getLogger()



class CmdLineError(Exception):
    pass

class CommandError(Exception):
    pass

