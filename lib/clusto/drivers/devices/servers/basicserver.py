from clusto.drivers.base import Device
from clusto.drivers.devices import PortMixin

class BasicServer(Device, PortMixin):
    """
    server
    """

    _clustoType = "server"
    _driverName = "basicserver"

    _properties = {'model':None,
                   'manufacturer':None}

    def addHD(self, size):
        """
        Add another HD to this server
        """
        pass
    
    
class BasicVirtualServer(Device):
    _clustoType = "server"
    _driverName = "basicvirtualserver"

    
    
        


