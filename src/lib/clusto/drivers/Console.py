
from clust.drivers import Thing, Part


class ConsoleServer(Thing, N):

    meta_attrs = {'clustotype': 'consoleserver'}



class OpenGearConsoleServer(ConsoleServer):

    meta_attrs = {'vendor': 'opengear' }


class ConsolePort(Part):
    
    pass
