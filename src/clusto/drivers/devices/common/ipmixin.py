"""
IPMixin is a basic mixin to be used by devices that can be assigned IPs
"""

import re

import clusto

from clusto.drivers.resourcemanagers import IPManager

from clusto.exceptions import ConnectionException,  ResourceException


class IPMixin:

    def addIP(self, ip=None, ipman=None):

        if not ip and not ipman:
            raise ResourceException('If no ip is specified then an ipmanager must be specified')

        elif ip:
            
            if not ipman:
                ipman = IPManager.getIPManager(ip)

            return ipman.allocate(self, ip)
        else:
            return ipman.allocate(self)
            
            
        
    def hasIP(self, ip):

        ipman = IPManager.getIPManager(ip)

        return self in ipman.owners(ip)
    
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

        if deallocate:
            ipman.deallocate(self, keyname, value)
