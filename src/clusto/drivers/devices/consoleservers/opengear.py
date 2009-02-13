
from basicconsoleserver import BasicConsoleServer


class OpenGearCM4148(BasicConsoleServer):

    _driverName = 'opengearcm4148'

    _portmeta = { 'pwr-nema-5' : { 'numports':1, },
		  'nic-eth' : { 'numports':1, },
		  'console-serial' : { 'numports':48, },
		  }


