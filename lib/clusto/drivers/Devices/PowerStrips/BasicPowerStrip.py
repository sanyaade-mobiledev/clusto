
from clusto.drivers.Base import Device, ResourceManagerMixin
from clusto.drivers.common import PortMixin

class BasicPowerStrip(PortMixin, ResourceManagerMixin, Device):
    """
    Basic power strip Driver.
    """

    _clustoType = "powerstrip"
    _driverName = "basicpowerstrip"
    

    _properties = { 'maxport': 20,
                    'minport': 1 }
    
