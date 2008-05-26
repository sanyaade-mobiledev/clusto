from clusto.drivers.Base import Device

class BasicServer(Device):
    """
    server
    """

    _clustoType = "server"
    _driverName = "basicserver"

    _properties = ('model', 'manufacturer')

    def addHD(self, size):
        """
        Add another HD to this server
        """
        pass
    
    
class BasicVirtualServer(Device):
    _clustoType = "server"
    _driverName = "basicvirtualserver"

    
    
        


