

import clusto
from clusto.drivers.base import Driver
from clusto.schema import VERSION

# incrementing the first number means a major schema change
# incrementing the second number means a change in a driver's storage details


class ClustoMeta(Driver):
    """
    Holds meta information about the clusto database
    """

    _properties = {'version':None}

    _clustoType = "clustometa"
    _driverName = "clustometa"


    def __init__(self): #, name=None, entity=None, *args, **kwargs):

        name = 'clustometa'
        try:
            meta = clusto.getByName(name)
            self = meta
        except LookupError:
            super(ClustoMeta, self).__init__(name)
            self.version = VERSION
            

        
