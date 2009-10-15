
from clusto.drivers.base import Device
from clusto.drivers.devices.common import PortMixin

class BasicPowerStrip(PortMixin, Device):
    """
    Basic power strip Driver.
    """

    _clusto_type = "powerstrip"
    _driver_name = "basicpowerstrip"
    

    
    _portmeta = { 'pwr-nema-5' : { 'numports':8, }, 
                  }
