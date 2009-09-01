"""
Server Technology Power Strips

"""


from basicpowerstrip import BasicPowerStrip

class PowerTowerXM(BasicPowerStrip):
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



    _portmap = {'aa1':0,'aa2':1,'aa3':2,'aa4':3,'aa5':4,'aa6':5,'aa7':6,'aa8':7,
                'ab1':8,'ab2':9,'ab3':10,'ab4':11,'ab5':12,'ab6':13,'ab7':14,
                'ab8':15,'ba1':16,'ba2':17,'ba3':18,'ba4':19,'ba5':20,'ba6':21,
                'ba7':22,'ba8':23,'bb1':24,'bb2':25,'bb3':26,'bb4':27,'bb5':28,
                'bb6':29,'bb7':30,'bb8':31,
                }

    def _ensurePortNum(self, porttype, portnum):
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
            


        

