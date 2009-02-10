
from clusto.drivers.base import Device
from clusto.drivers.devices.common import PortMixin

class BasicNetworkSwitch(PortMixin, Device):
    """
    Basic network switch driver
    """

    _clustoType = 'networkswitch'
    _driverName = 'basicnetworkswitch'


    _portmeta = {'pwr' : {'numports':1},
		 'eth' : {'numports':24}}


