"""
PortMixin is a basic mixin to be used with devices that have ports
"""

import re

import clusto
from clusto.drivers.base import ResourceManagerMixin
from clusto.exceptions import ConnectionException

class PortMixin:

    
    # _portmeta = { 'porttype' : {'numports': 10 }}

    _portmeta = { 'pwr' : { 'numports':1, },
		  'eth' : { 'numports':2, },
		  }


    def _checkPort(self, porttype, portnum):
	if not self.portExists(porttype, portnum):
	    raise TypeError("No port %s:%d exists on %s."
			    % (porttype, portnum, self.name))

    def _portKey(self, porttype):
	
	return 'port-' + porttype
    

    def connectPorts(self, porttype, srcportnum, dstdev, dstportnum):
	"""connect a local port to a port on another device
	"""


	for dev, num in [(self, srcportnum), (dstdev, dstportnum)]:
	    if not hasattr(dev, 'portExists'):
		msg = "%s has no ports."
		raise ConnectionException(msg % (dev.name))
	    if not dev.portExists(porttype, num):
		msg = "port %s:%d doesn't exist on %s"
		raise ConnectionException(msg % (porttype, num, dev.name))

	
	    if not dev.portFree(porttype, num):
		msg = "port %s%d on %s is already in use"
		raise ConnectionException(msg % (porttype, num, dev.name))


	self.setPortAttr('connection', dstdev, porttype, srcportnum)
	self.setPortAttr('otherportnum', dstportnum, porttype, srcportnum)
	
	dstdev.setPortAttr('connection', self, porttype, dstportnum)
	dstdev.setPortAttr('otherportnum', srcportnum, porttype, dstportnum)


    def disconnectPort(self, porttype, portnum):
	"""disconnect both sides of a port"""


	if not self.portFree(porttype, portnum):

	    dev = self.getConnected(porttype, portnum)
	    
	    otherportnum = self.getPortAttr('otherportnum', porttype, portnum)
	    
	    clusto.beginTransaction()
	    try:
		dev.delPortAttr('connection', porttype, otherportnum)
		dev.delPortAttr('otherportnum', porttype, otherportnum)
		
		self.delPortAttr('connection', porttype, portnum)
		self.delPortAttr('otherportnum', porttype, portnum)
	    except Exception, x:
		clusto.rollbackTransaction()
		raise x
	    

    def getConnected(self, porttype, portnum):
	"""return the device that the given porttype/portnum is connected to"""

 	if not self.portExists(porttype, portnum):
	    msg = "port %s:%d doesn't exist on %s"
	    raise ConnectionException(msg % (porttype, portnum, self.name))
	    

	return self.getPortAttr('connection', porttype, portnum)
	    

    def portsConnectable(self, porttype, srcportnum, dstdev, dstportnum):
	"""test if the ports you're trying to connect are compatible.
	"""

	return (self.portExists(porttype, srcportnum) 
		and dstdev.portExists(porttype, dstportnum))
 
    def portExists(self, porttype, portnum):
	"""return true if the given port exists on this device"""
	
  	if ((porttype in self._portmeta) 
	    and portnum >= 0
	    and portnum < self._portmeta[porttype]['numports']):
	    return True
	else:
	    return False

    def portFree(self, porttype, portnum):
	"""return true if the given porttype and portnum are not in use"""
	
	if (not self.portExists(porttype, portnum) or
	    self.hasAttr(key=self._portKey(porttype), numbered=portnum, 
			 subkey='connection')):
	    return False
	else:
	    return True
	

    def setPortAttr(self, key, value, porttype, portnum):
	"""set an attribute on the given port"""

	self._checkPort(porttype, portnum)

	self.setAttr(key=self._portKey(porttype),
		     numbered=portnum,
		     subkey=key,
		     value=value)


    def delPortAttr(self, key, porttype, portnum):
	"""delete an attribute on the given port"""

	self._checkPort(porttype, portnum)

	self.delAttrs(key=self._portKey(porttype),
		      numbered=portnum,
		      subkey=key)
		     
    def getPortAttr(self, key, porttype, portnum):
	"""set an attribute on the given port"""

	self._checkPort(porttype, portnum)

	attr = self.attrs(key=self._portKey(porttype),
			   numbered=portnum,
			   subkey=key)

	if len(attr) > 1:
	    raise ConnectionException("Somehow more than one attribute named %s is associated with port %s:%d on %s"
				      % (key, porttype, portnum, self.name))

	elif len(attr) == 1:
	    return attr[0].value

	else:
	    return None
	    
    @property
    def portInfo(self):
	"""return a list of tuples containing port information for this device
	
	format:
	  [ ('porttype', portnum, <connected device>, <port connected to>), ... ]
	"""

	portinfo = []
	for ptype in self.portTypes:
	    for n in range(self._portmeta[ptype]['numports']):
		t = (ptype, n, 
		     self.getPortAttr('connection', ptype, n),
		     self.getPortAttr('otherportnum', ptype, n))
		portinfo.append(t)

	return portinfo

    
    @property
    def freePorts(self):
	
	return [(pinfo[0], pinfo[1]) for pinfo in self.portInfo if pinfo[3] == None]

    @property
    def connectedPorts(self, porttype):
	raise NotImplemented()

    @property
    def portTypes(self):
	return self._portmeta.keys()


    
    


