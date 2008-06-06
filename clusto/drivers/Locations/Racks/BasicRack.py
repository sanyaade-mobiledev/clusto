
import re
from clusto.drivers.Base import ResourceManagerMixin, Location, Device

class BasicRack(ResourceManagerMixin, Location):
    """
    Basic rack driver.
    """

    _clustoType = "rack"
    _driverName = "basicrack"

    _properties = {'maxu':45}
    
    ruRegex = re.compile('RU(\d)')


    def _uAvailable(self, num):
        return self.hasAttr('RU' + str(num))
        
    def checkType(self, resource):
        """
        make sure rack locations names are of the form RU##

        ex. RU20

        ## should not exceed maxU
        
        """
        
        check = self.ruRegex.match(resource)
        if check:
            num = int(check.group(1))
            if num >= self.maxu:
                return False

            return True
            
        return False
    
    def addDevice(self, device, rackU):

        if not isinstance(device, Device):
            raise TypeError("You can only add Devices to a rack.  %s is a"
                            " %s" % (device.name, str(device.__class__)))

        if not isinstance(rackU, int):
            raise TypeError("a rackU must be an Integer")

        
        
        self.allocate(device, 'RU' + str(rackU))

        
