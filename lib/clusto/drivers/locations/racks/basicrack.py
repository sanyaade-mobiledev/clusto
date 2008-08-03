
import re
from clusto.drivers.base import ResourceManagerMixin, Location, Device

class BasicRack(ResourceManagerMixin, Location):
    """
    Basic rack driver.
    """

    _clustoType = "rack"
    _driverName = "basicrack"

    _properties = {'minu':1,
                   'maxu':45}
    
    ruRegex = re.compile('RU(\d+)')


    def _uAvailable(self, num):
        return self.hasAttr(self.runame(num))

    @classmethod
    def ruName(self, num):

        return 'RU%d' % num

    @classmethod
    def ruNum(self, ru):
        """
        take an runame and turn it into an integer.
        """
        return int(self.ruRegex.match(ru).group(1))
    
    def checkType(self, resource):
        """
        make sure rack locations names are of the form RU##

        ex. RU20

        ## should not exceed maxU
        
        """

        check = self.ruRegex.match(resource)

        if check:
            num = int(check.group(1))
            if num > self.maxu or num < self.minu:
                retval = False
                
            else:
                retval = True
        else:
            retval = False
            
        return retval
    
    def addDevice(self, device, rackU):
        if not isinstance(device, Device):
            raise TypeError("You can only add Devices to a rack.  %s is a"
                            " %s" % (device.name, str(device.__class__)))

        if not isinstance(rackU, int) and not isinstance(rackU, list):
            raise TypeError("a rackU must be an Integer or List of Integers.")


        if isinstance(rackU, list):
            for U in rackU:
                if not isinstance(U, int):
                    raise TypeError("a rackU must be an Integer or List of Integers.")

        if isinstance(rackU, int):
            rackU = [rackU]
            
        rau = self.getRackAndU(device)
        if rau != None:
            raise Exception("%s is already in rack %s"
                            % (device.name, rau['rack'].name))


        # do U checks
        for U in rackU:
            if U > self.maxu:
                raise TypeError("the rackU must be less than %d." % self.maxu)
            if U < 0:
                raise TypeError("RackUs may not be negative.")

        rackU.sort()
        last = rackU[0]
        for i in rackU[1:]:
            if i == last:
                raise TypeError("you can't list the same U twice.")
            if (i-1) != (last):
                raise TypeError("a device can only occupy multiple Us if they're adjacent.")
            last = i

        for U in rackU:
            self.allocate(device, self.ruName(U))

        
    def getDeviceIn(self, rackU):

        owners = self.owners(self.ruName(rackU))

        if len(owners) > 1:
            raise Exception('Somehow there is more than one thing in %s.'
                            'Only one of these should be in this space in the '
                            'rack: %s' % (self.ruName(rackU),
                                          ','.join([x.name for x in owners])))
        if owners:
            return owners[0]
        
        return None

    @classmethod
    def getRackAndU(self, device):
        """
        Get the rack and rackU for a given device.

        returns a tuple of (rack, u-number)
        """

        refs = device.references(clustotype=self._clustoType)

        if refs:
            return {'rack':refs[0].entity,  'RU':[self.ruNum(x.key)
                                                  for x in refs]}
        else:
            
            return None
