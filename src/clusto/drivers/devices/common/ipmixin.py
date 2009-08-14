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
    
