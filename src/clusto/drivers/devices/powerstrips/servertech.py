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

    _drivername = "powertowerxm"

    _properties = {'withslave':0}


    _portmeta = { 'pwr' : { 'numports':16, },
		  'eth' : { 'numports':1, },
		  }


    def _ensurePortNum(self, porttype, num):
	pass

    def _portmap(self, porttype, portnum):
	"""map powertower port names to clusto port numbers"""
	pass



	

