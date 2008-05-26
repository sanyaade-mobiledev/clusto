

import re
from clusto.drivers.Base import ResourceManager


class RUManager(ResourceManager):
    """
    Manage the U locations in a rack
    """
    _driverName = 'rumanager'
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
