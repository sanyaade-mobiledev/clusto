from clusto.drivers.Base import Thing
from clusto.drivers.Net import NICMixin


class Server(Thing, NICMixin):

    meta_attrs = { 'clustotype': 'server' }


    #required_attrs = ['serialnumber']
        



class ConsoleServer(Thing):
    
    meta_attrs = { 'clustotype': 'consoleserver' }

