
from clusto.drivers.Base import Device

class BasicPowerStrip(Device):
    """
    Basic power strip Driver.
    """

    _clustoType = "powerstrip"
    _driverName = "basicpowerstrip"
    

    _properties = { 'maxport': 20,
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
