
from clusto.drivers.base import Device
from clusto.drivers.devices.common import PortMixin

class BasicPowerStrip(PortMixin, Device):
    """
    Basic power strip Driver.
    """

    _clustoType = "powerstrip"
    _driverName = "basicpowerstrip"
    

    
