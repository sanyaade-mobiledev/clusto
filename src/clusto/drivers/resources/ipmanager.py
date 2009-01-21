from clusto.drivers import ResourceManager, ResourceTypeException
from clusto.exceptions import ResourceNotAvailableException

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

	    self.__ipy = IPy.IP(''.join([str(self.baseip), '/', self.netmask]),
				make_net=True)


	return self.__ipy

    def ensureType(self, resource, numbered=True):

	"""check that the given ip falls within the range managed by this manager"""

	try:
	    if not isinstance(numbered, bool) and isinstance(numbered, int):
		ip = IPy.IP(numbered)
	    else:
		ip = IPy.IP(resource)
	except ValueError:
	    raise ResourceTypeException("%s is not a valid ip."
					% resource)

	if self.baseip and (ip not in self.ipy):
	    raise ResourceTypeException("The ip %s is out of range for this IP manager.  Should be in %s/%s"
					% (str(resource), self.baseip, self.netmask))


	return ('ip', ip.int())


    def allocator(self):
	"""allocate IPs from this manager"""

	if self.baseip is None:
	    raise ResourceTypeException("Cannot generate an IP for an ipManager with no baseip")

	lastip = self.attrQuery('_lastip')
		
	if not lastip:
	    startip=int(self.ipy.net().int() + 1)
	else:
	    startip = lastip[0].value


	
	## generate new ips the slow naive way
	nextip = long(startip)
	gateway = IPy.IP(self.gateway).int()
	endip = self.ipy.broadcast().int()

	for i in range(2):
	    while nextip < endip:

		if nextip == gateway:
		    nextip += 1
		    continue

		if self.available(nextip):
		    self.setAttr('_lastip', nextip)
		    return self.ensureType(nextip)
		else:
		    nextip += 1
	    
	    # check from the beginning again in case an earlier ip
	    # got freed
		    
	    nextip = long(self.ipy.net().int() + 1)
	    
	raise ResourceNotAvailableException("out of available ips.")
	    
