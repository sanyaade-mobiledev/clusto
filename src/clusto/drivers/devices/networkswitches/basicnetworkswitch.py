
from clusto.drivers.base import Device
from clusto.drivers.devices.common import PortMixin

class BasicNetworkSwitch(PortMixin, Device):
    """
    Basic network switch driver
    """

    _clustoType = 'networkswitch'
    _driverName = 'basicnetworkswitch'


    _portmeta = {'pwr-nema-5' : {'numports':1},
                 'nic-eth' : {'numports':24}}


