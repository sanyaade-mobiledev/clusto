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

	lastip = self.attrs('_lastip')
	
	if not lastip:
	    startip=self.ipy.net().int() + 1

	    if not self.attrs('ip', numbered=startip):
		self.setAttr('_lastip', startip)
		return ('ip', startip, None)
	else:
	    startip = lastip[0]


	ipcounter = 1 # we already know the first address is used up
	iplen = self.ipy.len() # so I know when I've tried all IPs
	workingip = startip

	
	
	raise NotImplemented("Still working on allocating free IPs")

	    
