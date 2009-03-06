"""
PortMixin is a basic mixin to be used with devices that have ports
"""

import re

import clusto

from clusto.drivers.resourcemanagers import IPManager

from clusto.exceptions import ConnectionException

class PortMixin:

    
    # _portmeta = { 'porttype' : {'numports': 10 }}

    _portmeta = { 'pwr-nema-5' : { 'numports':1, },
                  'nic-eth' : { 'numports':2, },
                  }


    def _portKey(self, porttype):
        
        return '_port-' + porttype
    
    def _ensurePortNum(self, porttype, num):


        if not self._portmeta.has_key(porttype) \
                or not isinstance(num, int) \
                or num < 0 \
                or num >= self._portmeta[porttype]['numports']:

            msg = "No port %s:%s exists on %s." % (porttype, str(num), self.name)
                    
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


        self.setPortAttr(porttype, srcportnum, 'connection', dstdev)
        self.setPortAttr(porttype, srcportnum, 'otherportnum', dstportnum)
        
        dstdev.setPortAttr(porttype, dstportnum, 'connection', self)
        dstdev.setPortAttr(porttype, dstportnum, 'otherportnum', srcportnum)


    def disconnectPort(self, porttype, portnum):
        """disconnect both sides of a port"""

        portnum = self._ensurePortNum(porttype, portnum)

        if not self.portFree(porttype, portnum):

            dev = self.getConnected(porttype, portnum)
            
            otherportnum = self.getPortAttr(porttype, portnum, 'otherportnum')
            
            clusto.beginTransaction()
            try:
                dev.delPortAttr(porttype, otherportnum, 'connection')
                dev.delPortAttr(porttype, otherportnum, 'otherportnum')
                
                self.delPortAttr(porttype, portnum, 'connection')
                self.delPortAttr(porttype, portnum, 'otherportnum')
            except Exception, x:
                clusto.rollbackTransaction()
                raise x
            

    def getConnected(self, porttype, portnum):
        """return the device that the given porttype/portnum is connected to"""

        portnum = self._ensurePortNum(porttype, portnum)

        if not self.portExists(porttype, portnum):
            msg = "port %s:%d doesn't exist on %s"
            raise ConnectionException(msg % (porttype, portnum, self.name))
            

        return self.getPortAttr(porttype, portnum, 'connection')
            

    def portsConnectable(self, porttype, srcportnum, dstdev, dstportnum):
        """test if the ports you're trying to connect are compatible.
        """

        return (self.portExists(porttype, srcportnum) 
                and dstdev.portExists(porttype, dstportnum))
 
    def portExists(self, porttype, portnum):
        """return true if the given port exists on this device"""
        
        if ((porttype in self._portmeta)):
            try:
                portnum = self._ensurePortNum(porttype, portnum)
                return True
            except ConnectionException:
                return False
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
        

    def addPortAttr(self, porttype, portnum, key, value):
        """add an attribute on the given port"""

        portnum = self._ensurePortNum(porttype, portnum)

        self.addAttr(key=self._portKey(porttype),
                     numbered=portnum,
                     subkey=key,
                     value=value)

    def setPortAttr(self, porttype, portnum, key, value):
        """set an attribute on the given port"""

        portnum = self._ensurePortNum(porttype, portnum)

        self.setAttr(key=self._portKey(porttype),
                     numbered=portnum,
                     subkey=key,
                     value=value)


    def delPortAttr(self, porttype, portnum, key, value=()):
        """delete an attribute on the given port"""

        portnum = self._ensurePortNum(porttype, portnum)

        if value is ():
            self.delAttrs(key=self._portKey(porttype),
                          numbered=portnum,
                          subkey=key)
        else:

            self.delAttrs(key=self._portKey(porttype),
                          numbered=portnum,
                          subkey=key,
                          value=value)
            
                     
    def getPortAttr(self, porttype, portnum, key):
        """get an attribute on the given port"""

        portnum = self._ensurePortNum(porttype, portnum)

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
                portinfo[ptype][n] = {'connection': self.getPortAttr(ptype, n, 'connection'),
                                      'otherportnum': self.getPortAttr(ptype, n, 'otherportnum')}

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


    def bindIPtoPort(self, ip, porttype, portnum):
        """bind an IP to a port

        @param ip: the ip you want to bind to a port
        @type ip: either an integer, IPy, string, Attribute from an IPManager

        @param porttype: the port type
        @type porttype: a porttype string

        @param portnum: the number of the port
        @type portnum: integer
        """
        
        if not porttype.startswith('nic-'):
            raise ConnectionException("Cannot bind IP to a non-network port.")


        ipman = IPManager.getIPManager(ip)


        if self in ipman.owners(ip):
            keyname, value = ipman.ensureType(ip)

        elif ipman.available(ip):

            attr = ipman.allocate(self, ip)

            keyname = attr.subkey
            value = attr.number
            
        else:
            raise ConnectionException("IP %s is not available to you." % str(ip))
        
        self.setPortAttr(porttype, portnum, keyname, value)
        ipman.lockResource(self, keyname, value)

    def unbindIPfromPort(self, ip, porttype, portnum, deallocate=True):
        """unbind an IP from a port

        @param ip: the ip you want to unbind from the port
        @type ip: either an integer, IPy, string, Attribute from an IPManager

        @param porttype: the port type
        @type porttype: a porttype string

        @param portnum: the number of the port
        @type portnum: integer
        """
        
        if not porttype.startswith('nic-'):
            raise ConnectionException("Cannot bind IP to a non-network port.")


        ipman = IPManager.getIPManager(ip)


        if self in ipman.owners(ip):
            keyname, value = ipman.ensureType(ip)

        elif ipman.available(ip):

            attr = ipman.allocate(ip)

            keyname = attr.subkey
            value = attr.number
            
        else:
            raise ConnectionException("IP %s is not available to you." % str(ip))

        self.delPortAttr(porttype, portnum, keyname, value)
        ipman.unlockResource(self, keyname, value)
        ipman.deallocate(self, keyname, value)
