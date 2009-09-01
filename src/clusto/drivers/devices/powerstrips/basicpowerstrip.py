
from clusto.drivers.base import Device
from clusto.drivers.devices.common import PortMixin

class BasicPowerStrip(PortMixin, Device):
    """
    Basic power strip Driver.
    """

    _clusto_type = "powerstrip"
    _driverName = "basicpowerstrip"
    

    
    _portmeta = { 'pwr-nema-5' : { 'numports':8, }, 
                  'nic-eth': {'numports':1, },
                  'console-serial': {'numports':1}
                  }
