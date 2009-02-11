"""
PortMixin is a basic mixin to be used with devices that have ports
"""

import re

import clusto
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
	
	return '_port-' + porttype
    
    def _ensurePortNum(self, porttype, num):

	if not isinstance(num, int):

	    if hasattr(self, '_portmap'):
		num = self._portmap(porttype, num)
	    else:
		msg = "passed in %s but %s has no port map to translate " \
		      "into an integer" % (num, self.name)
		    
		raise ConnectionException(msg)
		
	return num

    def connectPorts(self, porttype, srcportnum, dstdev, dstportnum):
	"""connect a local port to a port on another device
	"""


	for dev, num in [(self, srcportnum), (dstdev, dstportnum)]:

	    if not hasattr(dev, 'portExists'):
		msg = "%s has no ports."
		raise ConnectionException(msg % (dev.name))

	    num = dev._ensurePortNum(porttype, num)

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

	portnum = self._ensurePortNum(porttype, portnum)

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

	portnum = self._ensurePortNum(porttype, portnum)

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
	
  	if ((porttype in self._portmeta)):
	    portnum = self._ensurePortNum(porttype, portnum)

	    if portnum >= 0 and portnum < self._portmeta[porttype]['numports']:
		return True
	else:
	    return False

    def portFree(self, porttype, portnum):
	"""return true if the given porttype and portnum are not in use"""
	
	portnum = self._ensurePortNum(porttype, portnum)

	if (not self.portExists(porttype, portnum) or
	    self.hasAttr(key=self._portKey(porttype), numbered=portnum, 
			 subkey='connection')):
	    return False
	else:
	    return True
	

    def setPortAttr(self, key, value, porttype, portnum):
	"""set an attribute on the given port"""

	portnum = self._ensurePortNum(porttype, portnum)

	self._checkPort(porttype, portnum)

	self.setAttr(key=self._portKey(porttype),
		     numbered=portnum,
		     subkey=key,
		     value=value)


    def delPortAttr(self, key, porttype, portnum):
	"""delete an attribute on the given port"""

	portnum = self._ensurePortNum(porttype, portnum)

	self._checkPort(porttype, portnum)

	self.delAttrs(key=self._portKey(porttype),
		      numbered=portnum,
		      subkey=key)
		     
    def getPortAttr(self, key, porttype, portnum):
	"""get an attribute on the given port"""

	self._checkPort(porttype, portnum)

	attr = self.attrs(key=self._portKey(porttype),
			  numbered=portnum,
			  subkey=key)

	if len(attr) > 1:
	    raise ConnectionException("Somehow more than one attribute named "
				      "%s is associated with port %s:%d on %s"
				      % (key, porttype, portnum, self.name))

	elif len(attr) == 1:
	    return attr[0].value

	else:
	    return None
	    
    @property
    def portInfo(self):
	"""return a list of tuples containing port information for this device
	
	format:
	    portInfo[<porttype>][<portnum>][<portattr>]
	"""

	portinfo = {}
	for ptype in self.portTypes:
	    portinfo[ptype]={}
	    for n in range(self._portmeta[ptype]['numports']):
		portinfo[ptype][n] = {'connection': self.getPortAttr('connection', ptype, n),
				      'otherportnum': self.getPortAttr('otherportnum', ptype, n)}

	return portinfo

    @property
    def portInfoTuples(self):
	"""return port information as a list of tuples that are suitble for use
	as *args to connectPorts

	format:
	  [ ('porttype', portnum, <connected device>, <port connected to>), ... ]
	"""
	
	t = []
	d = self.portInfo
	for porttype, numdict in d.iteritems():
	    for num, stats in numdict.iteritems():
		t.append((porttype, num, 
			  stats['connection'], stats['otherportnum']))
	
	return t

			 

    
    @property
    def freePorts(self):
	
	return [(pinfo[0], pinfo[1]) for pinfo in self.portInfoTuples if pinfo[3] == None]

    @property
    def connectedPorts(self):
	"""Return a list of connected ports"""

	pdict = {}
	for ptype in self.portTypes:

	    portlist = [a.number for a in self.attrs(self._portKey(ptype), 
						     subkey='connection')]
	    portlist.sort()
	    pdict[ptype] = portlist

	return pdict

    @property
    def portTypes(self):
	return self._portmeta.keys()


    
    


