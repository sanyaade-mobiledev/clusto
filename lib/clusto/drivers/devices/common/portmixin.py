"""
PortMixin is a basic mixin to be used with devices that have ports
"""

from clusto.drivers.base import ResourceManagerMixin

class PortMixin:

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
    
    def disconnectDevice(self, device):
        
        self.deallocate(device)

