
from clusto.drivers.Base import Device, ResourceManagerMixin


class BasicNetworkSwitch(ResourceManagerMixin, Device):
    """
    Basic network switch driver
    """

    _clustoType = 'networkswitch'
    _driverName = 'basicnetworkswitch'

    _properties = { 'maxport': 48,
                    'minport': 1 }
    
    def checkType(self, portnumber):
        """
        Make sure that the portnumber given is valid and within the appropriate
        range.
        """

        if (not isinstance(portnumber, int)
            or portnumber < minport
            or portnumber > maxport):
            raise TypeError("portnumber must be an integer between %d and %d"
                            % (self.minport, self.maxport))

        return True

    

        
    def connectDevice(self, device, port):
        """
        Connect a given device to a given port.
        """

        self.allocate(device, port)
