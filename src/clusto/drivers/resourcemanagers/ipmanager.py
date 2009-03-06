import clusto
from clusto.schema import Attribute

from clusto.drivers import ResourceManager, ResourceTypeException
from clusto.exceptions import ResourceNotAvailableException, ResourceException

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
            if not isinstance(numbered, bool) and isinstance(int(numbered), int):
                ## add here to map unsigned ints from IPs to signed ints of python
                ip = IPy.IP(int(numbered+2147483648))
            else:
                ip = IPy.IP(resource)           
        except ValueError:
            raise ResourceTypeException("%s is not a valid ip."
                                        % resource)

        if self.baseip and (ip not in self.ipy):
            raise ResourceTypeException("The ip %s is out of range for this IP manager.  Should be in %s/%s"
                                        % (str(resource), self.baseip, self.netmask))


        return ('ip', int(ip.int()-2147483648))


    def allocator(self):
        """allocate IPs from this manager"""

        if self.baseip is None:
            raise ResourceTypeException("Cannot generate an IP for an ipManager with no baseip")

        lastip = self.attrQuery('_lastip')
                
        if not lastip:
            # I subtract 2147483648 to keep in int range
            startip=int(self.ipy.net().int() + 1) - 2147483648 
        else:
            startip = lastip[0].value


        
        ## generate new ips the slow naive way
        nextip = int(startip)
        gateway = IPy.IP(self.gateway).int() - 2147483648
        endip = self.ipy.broadcast().int() - 2147483648

        for i in range(2):
            while nextip < endip:

                if nextip == gateway:
                    nextip += 1
                    continue

                if self.available('ip', nextip):
                    self.setAttr('_lastip', nextip)
                    return self.ensureType('ip', nextip)
                else:
                    nextip += 1
            
            # check from the beginning again in case an earlier ip
            # got freed
                    
            nextip = int(self.ipy.net().int() + 1)
            
        raise ResourceNotAvailableException("out of available ips.")

    @classmethod
    def getIPManager(cls, ip):
        """return a valid ip manager for the given ip.

        @param ip: the ip
        @type ip: integer, string, or IPy object

        @return: the appropriate IP manager from the clusto database
        """

        ipman = None
        if isinstance(ip, Attribute):
            ipman = ip.entity
            return ipman

        for ipmantest in clusto.getEntities(clustotypes=[cls]):
            try:
                ipmantest.ensureType(ip)
            except ResourceTypeException:
                pass

            ipman = ipmantest
            break
        

        if not ipman:
            raise ResourceException("No resource manager for %s exists."
                                    % str(ip))
        
        return ipman
        

