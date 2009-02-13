from clusto.drivers.base import Device
from clusto.drivers.devices import PortMixin

class BasicServer(PortMixin, Device):
    """
    server
    """

    _clustoType = "server"
    _driverName = "basicserver"

    _properties = {'model':None,
                   'manufacturer':None}

    _portmeta = {'pwr-nema-5': {'numports':1},
		 'nic-eth': {'numports':2},
		 'console-serial' : { 'numports':1, }
		 }

    def addHD(self, size):
        """
        Add another HD to this server
        """
        pass
    
    
class BasicVirtualServer(Device):
    _clustoType = "server"
    _driverName = "basicvirtualserver"

    
    
        


