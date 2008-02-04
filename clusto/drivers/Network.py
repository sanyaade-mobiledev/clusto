from clusto.drivers.Base import Driver
import IPy

IPy.check_addr_prefixlen = False

class IP(Driver):
    _driverName = "ip"

    _properties = ('ip', 'netmask', 'gateway', 'dns',)

    
class IPMixin:

    def listIPs(self):
        pass

    def addIP(self):
        pass
    
    def iplist(self):
        pass
    
class NetBlock(Driver):

    _driverName = "netblock"

    _properties = ('ip', 'netmask', 'gateway', 'dns',)

    def allocateIP(self, IP=None):
        pass

    def releaseIP(self, IP):
        pass

    def _allocatedIPs(self):
        pass

    def _freeIPs(self):
        pass
    
class NicMixin:
    """

    nic0_macaddr
    nic0_ip
    """
    
    def listNics(self):
        pass
    
    def addNic(self):
        pass

    def delNic(self):
        pass


class Nic(Driver):
    """
    Network Interface Card
    """

    _driverName = "nic"
    
    def _setMacAddr(self, mac):

        self.setAttr('macaddr', mac)

    def _getMacAddr(self):
        return self.getAttr('macaddr', default=None)

    macaddr = property(_getMacAddr, _setMacAddr)
        
    def setIP(self, IP):
        pass
    
class Bridge(Driver):
    _driverName = "bridge"
