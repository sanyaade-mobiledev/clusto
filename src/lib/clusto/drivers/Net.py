from clusto.drivers import Thing
from clusto.drivers import Part

import IPy

class Network(Thing):
    """
    represents a network block
    """

    meta_attrs = {'clustotype': 'network'}

    required_attrs = ['netip', 'netmask',]

    @classmethod
    def allocateIP(self, something, ipaddr=None):
        """
        Give a Thing an IP.  If an IP is not specified then an unused one from
        this network block will be given.
        """

        if ipaddr:
            newip = IP(ipaddr, self.getAttr('netmask'))
            
            self.connect(newip)
            something.connect(newip)
        else:
            # generate new unused ip
            pass


    def deallocateIP(self, something, ipaddr=None):
        """
        Take back an ip from something and return it to the available pool for
        this network.
        """
        pass
    
    def getFreeIP(self):
        pass

    def setDNS(self, dnsip):
        self.setAttr('dns', IPy.IP(dnsip).int())

    def setGateway(self, gwip):
        self.setAttr('gw', IPy.IP(gwip).int())

        

class IP(Thing):
    meta_attrs = {'custotype': 'ip' }
    
    required_attrs = ['ipaddr', 'netmask']

    

class NIC(Part):

    meta_attrs = {'clustotype': 'nic'}

    required_attrs = ['macaddr']

    #connectables = [Server, Port]


class NICMixin:

    mixin_nic_args = ['macaddrs']

    def addNIC(self, macaddr):
        self.connect(NIC(self.name, macaddr=macaddr))
    
    def getMACs(self):
        nics = filter(lambda x: isinstance(x, NIC), self.connections)

        return [ nic.getAttr('macaddr') for nic in nics ]

    def getNIC(self, macaddr):
        return filter(lambda x: x.getAttr('macaddr') == macaddr,
                      self.connections)[0]

class IPMixin:

    def getIP(self):
        """
        Return the first ip connected to this Thing.
        """

        
        iplist = filter(lambda x: isinstance(x, IP),
                        self.connections)

        return iplist and iplist[0] or None

    def setIP(self, ip):
        iplist = filter(lambda x: isinstance(x, IP),
                        self.connections)
        for i in iplist:
            self.disconnect(i)

        Network.allocateIP(self, ip)

    def addIP(self, ip):
        pass

    def delIP(self, ip):
        pass

    def releaseIP(self, ip):
        pass

