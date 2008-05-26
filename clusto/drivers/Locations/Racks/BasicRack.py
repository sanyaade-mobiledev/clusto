
import re
from clusto.drivers.Base import ResourceManagerMixin, Location, Device

class BasicRack(ResourceManagerMixin, Location):
    """
    Basic rack driver.
    """

    _clustoType = "rack"
    _driverName = "basicrack"


    ruRegex = re.compile('RU(\d)')

    maxU = 45

    
    def checkType(self, resource):
        """
        make sure rack locations names are of the form RU##

        ex. RU20

        ## should not exceed maxU
        
        """
        
        check = self.ruRegex.match(resource)
        if check:
            num = int(check.group(1))
            if num >= self.maxU:
                return False

            return True
            
        return False
    
    def addDevice(self, device):

        if not isinstance(device, Device):
            raise TypeError("You can only add Devices to a rack.  %s is a"
                            " %s" % (device.name, str(device.__class__)))


