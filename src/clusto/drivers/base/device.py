
from clusto.drivers.base import Driver

class Device(Driver):

    _properties = {'model':None,
                   'serialnum':None,
                   'manufacturer':None}

    _clustotype = "device"
    _driverName = "device"


    @classmethod
    def getBySerialNumber(self, serialnum):
        pass

    def _getHostname(self):
        """return a hostname set for this device or its entity name"""

        hostname = self.attrs("hostname", uniqattr=True)

        if hostname:
            return hostname[0].value
        else:
            return self.entity.name
        
    def _setHostname(self, name):

        self.setAttr("hostname", value=name, uniqattr=True)

    hostname = property(_getHostname, _setHostname)

    @property
    def FQDNs(self):
        """return the fully qualified domain names for this device"""

        return self.attrValues("fqdn")


    def addFQDN(self, fqdn):

        if not self.hasAttr("fqdn", numbered=True, value=fqdn):
            self.addAttr("fqdn", numbered=True, value=fqdn)

    def removeFQDN(self, fqdn):

        self.delAttrs("fqdn", numbered=True, value=fqdn)

        
        
