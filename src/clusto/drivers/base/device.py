
from clusto.drivers.base import Driver

class Device(Driver):

    _properties = {'model':None,
                   'serialnum':None,
                   'manufacturer':None}

    _clustotype = "device"
    _driver_name = "device"


    @classmethod
    def get_by_serial_number(self, serialnum):
        pass

    def _get_hostname(self):
        """return a hostname set for this device or its entity name"""

        hostname = self.attrs("hostname")

        if hostname:
            return hostname[0].value
        else:
            return self.entity.name
        
    def _set_hostname(self, name):

        self.set_attr("hostname", value=name)

    hostname = property(_get_hostname, _set_hostname)

    @property
    def fqdns(self):
        """return the fully qualified domain names for this device"""

        return self.attr_values("fqdn")


    def addfqdn(self, fqdn):
        """add a fully qualified domain name"""
        
        if not self.has_attr("fqdn", number=True, value=fqdn):
            self.add_attr("fqdn", number=True, value=fqdn)

    def removefqdn(self, fqdn):
        """remove a fully qualified domain name"""
        
        self.del_attrs("fqdn", number=True, value=fqdn)

        
        
