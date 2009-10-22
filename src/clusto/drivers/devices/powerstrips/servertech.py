"""
Server Technology Power Strips

"""


from basicpowerstrip import BasicPowerStrip
from clusto.drivers.devices.common import IPMixin


class PowerTowerXM(IPMixin, BasicPowerStrip):
    """
    Provides support for Power Tower XL/XM

    Power Port designations start with 1 at the upper left (.aa1) down to 32
    at the bottom right (.bb8).
    """

    _driver_name = "powertowerxm"

    _properties = {'withslave':0}


    _portmeta = { 'pwr-nema-L5': { 'numports':2 },
                  'pwr-nema-5' : { 'numports':16, },
                  'nic-eth' : { 'numports':1, },
                  'console-serial' : { 'numports':1, },
                  }



    _portmap = {'aa1':1,'aa2':2,'aa3':3,'aa4':4,'aa5':5,'aa6':6,'aa7':7,'aa8':8,
                'ab1':9,'ab2':10,'ab3':11,'ab4':12,'ab5':13,'ab6':14,'ab7':15,
                'ab8':16,'ba1':17,'ba2':18,'ba3':19,'ba4':20,'ba5':21,'ba6':22,
                'ba7':23,'ba8':24,'bb1':25,'bb2':26,'bb3':27,'bb4':28,'bb5':29,
                'bb6':30,'bb7':31,'bb8':32,
                }

    def _ensure_portnum(self, porttype, portnum):
        """map powertower port names to clusto port numbers"""

        if not self._portmeta.has_key(porttype):
            msg = "No port %s:%s exists on %s." % (porttype, str(num), self.name)
                    
            raise ConnectionException(msg)

        if isinstance(portnum, int):
            num = portnum
        else:
            if portnum.startswith('.'):
                portnum = portnum[1:] 
            
            if self._portmap.has_key(portnum):
                num = self._portmap[portnum]
            else:
                msg = "No port %s:%s exists on %s." % (porttype, str(num), 
                                                       self.name)
                    
                raise ConnectionException(msg)
 
        numports = self._portmeta[porttype]
        if self.withslave:
            if porttype in ['mains', 'pwr']:
                numports *= 2

        if num < 0 or num >= numports:
            msg = "No port %s:%s exists on %s." % (porttype, str(num), 
                                                   self.name)
                    
            raise ConnectionException(msg)



        return num
            


        

