
import os
import clusto

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
                       and not x.endswith('~'),
                       dirlist)

    
    return map(lambda x: os.path.join(path, x), available)


def getCommand(cmdname):

    for path in scriptpaths:

        scripts = listClustoScripts(path)

        for s in scripts:
            if s.split('-')[1].split('.')[0] == cmdname:
                return s


    return None
