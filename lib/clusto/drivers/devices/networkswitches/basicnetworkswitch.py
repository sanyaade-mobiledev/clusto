
from clusto.drivers.base import Device, ResourceManagerMixin
from clusto.drivers.devices.common import PortMixin

class BasicNetworkSwitch(PortMixin, ResourceManagerMixin, Device):
    """
    Basic network switch driver
    """

    _clustoType = 'networkswitch'
    _driverName = 'basicnetworkswitch'

    _properties = { 'maxport': 48,
                    'minport': 1 }
    
