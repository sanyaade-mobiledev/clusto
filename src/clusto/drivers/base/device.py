
from clusto.drivers.base import Driver

class Device(Driver):

    _properties = {'model':None,
                   'serialnum':None,
                   'manufacturer':None}

    _clustotype = "device"
    _driver_name = "device"


    @classmethod
    def getBySerialNumber(self, serialnum):
        pass

    def _getHostname(self):
        """return a hostname set for this device or its entity name"""

        hostname = self.attrs("hostname")

        if hostname:
            return hostname[0].value
        else:
            return self.entity.name
        
    def _setHostname(self, name):

        self.set_attr("hostname", value=name)

    hostname = property(_getHostname, _setHostname)

    @property
    def FQDNs(self):
        """return the fully qualified domain names for this device"""

        return self.attr_values("fqdn")


    def addFQDN(self, fqdn):
        """add a fully qualified domain name"""
        
        if not self.has_attr("fqdn", number=True, value=fqdn):
            self.add_attr("fqdn", number=True, value=fqdn)

    def removeFQDN(self, fqdn):
        """remove a fully qualified domain name"""
        
        self.delAttrs("fqdn", number=True, value=fqdn)

        
        
