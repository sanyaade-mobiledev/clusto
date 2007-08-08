from clusto.drivers.Base import Thing
from clusto.drivers.Net import NICMixin


class Server(Thing, NICMixin):

    meta_attrs = { 'clustotype': 'server' }


    #required_attrs = ['serialnumber']
        
    def addIP(self, nic, ip):
        """
        add an IP to this server
        """
        pass


    def getIPs(self):
        """
        returns the IPs associated with this server
        """
        pass

    def getConsole(self):
        pass




class ConsoleServer(Thing):
    
    meta_attrs = { 'clustotype': 'consoleserver' }

