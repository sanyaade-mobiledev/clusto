from clusto.drivers.Base import Thing, Part
import sys

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

        

class NIC(Part):
    """
    a single NIC
    """

    meta_attrs = {'clustotype': 'nic', }

    required_attrs = ['macaddr']

    #connectables = [Server, Port]

    
class NICMixin:

    mixin_nic_args = ['macaddrs']

    def numNICs(self):
        return len(self.connectedByType(NIC))
        
    def addNIC(self, macaddr):
        self.connect(NIC(self.name+'nic'+str(self.numNICs), macaddr=macaddr))
    
    def getMACs(self):
        nics = self.connectedByType(NIC)

        return [ nic.getAttr('macaddr') for nic in nics ]

    def getNIC(self, macaddr):

        retval = self.getConnectedMatching(AttributeDict({'macaddr':macaddr}))
                                
        return retval

class IP(Thing):
    """
    a single IP
    """
    meta_attrs = {'clustotype': 'ip' }
    
    required_attrs = ['ipaddr', 'netmask']

    def canConnectTo(self, thing):
        """
        IPs can only connect to things that are NICs or Networks
        """
        return thing.isOfType(NIC) or thing.isOfType(Network)


class IPMixin:
    """
    This Mixin contains helper functions for Things that may have IPs closely
    associated with them, like Servers, Routers, and Switches.
    """
    def getIP(self, allIPs=False):
        """
        Return the first ip connected to this Thing.
        """

        
        iplist = filter(lambda x: isinstance(x, IP),
                        self.connections)

        if iplist:
            return allIPs and iplist or iplist[0]
        else:
            return None

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

