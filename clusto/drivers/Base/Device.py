
from clusto.drivers.Base import Driver

class Device(Driver):

    _properties = ('model', 'serialnum', 'manufacturer',)

    _clustotype = "device"
    _driverName = "device"


