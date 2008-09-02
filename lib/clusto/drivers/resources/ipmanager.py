from clusto.drivers import ResourceManager, ResourceTypeException

import IPy

class IPManager(ResourceManager):
    """Resource Manager for IP spaces
    
    roughly follows the functionality available in IPy
    """


    _driverName="ipmanager"

    _properties = {'gateway': None,
		   'netmask': '255.255.255.255',
		   'baseip': None }

    _attrName = "ip"

    @property
    def ipy(self):
	if not hasattr(self, '__ipy'):

	    self.__ipy = IPy.IP(''.join([self.baseip, '/', self.netmask]))


	return self.__ipy

    def checkType(self, resource):
	"""check that the given ip falls within the range managed by this manager"""

	try:
	    ip = IPy.IP(resource)
	except ValueError:
	    raise ResourceTypeException("%s is not a valid ip."
					% resource)

	if self.baseip == None:
	    return ip.strDec()

	else:

	    if ip not in self.ipy:
		raise ResourceTypeException("The ip %s is out of range for this IP manager.  Should be in %s/%s"
					    % (str(resource), self.baseip, self.netmask))
	    else:
		return ip.strDec()

	    
	
