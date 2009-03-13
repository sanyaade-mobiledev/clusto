
from clusto.drivers import Device
from clusto.drivers.devices import PortMixin

class BasicConsoleServer(PortMixin, Device):
    """
    Basic console server Driver
    """

    _clustoType = 'consoleserver'
    _driverName = 'basicconsoleserver'

    
    _portmeta = { 'pwr-nema-5' : { 'numports':1, },
                  'nic-eth' : { 'numports':1, },
                  'console-serial' : { 'numports':24, },
                  }

    def connect(self, port, num):
        raise NotImplemented
