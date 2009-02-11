
from clusto.drivers import Device
from clusto.drivers.devices import PortMixin

class BasicConsoleServer(PortMixin, Device):
    """
    Basic console server Driver
    """

    _clustoType = 'consoleserver'
    _driverName = 'basicconsoleserver'

    
    _portmeta = { 'pwr' : { 'numports':1, },
		  'eth' : { 'numports':1, },
		  'ser' : { 'numports':24, },
		  }

