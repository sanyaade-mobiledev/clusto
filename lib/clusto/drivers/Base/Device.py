
from clusto.drivers.Base import Driver

class Device(Driver):

    _properties = {'model':None,
                   'serialnum':None,
                   'manufacturer':None}

    _clustotype = "device"
    _driverName = "device"


    @classmethod
    def getBySerialNumber(self, serialnum):
        pass
