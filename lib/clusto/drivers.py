
from schema import *

class ClustoType(Thing):

    __metaclass__ = ClustoThing
    
    clustotype = "clustotype"
    
    def __init__(self, name):

        Thing.__init__(self, name, type(self).clustotype)

class Server(ClustoType):

    clustotype = "server"

class PowerStrip(ClustoType):
    clustotype = "powerstrip"
    

class LoadBalancer(ClustoType):
    clustotype = "loadbalancer"

class Netscaler(LoadBalancer):

    metaattrs = { 'vendor': 'citrix' }
    pass



