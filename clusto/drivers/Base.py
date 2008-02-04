from clusto.schema import *
from clusto.exceptions import *
import clusto
from clusto.drivers.Mixins import *

DRIVERLIST = {}

class ClustoDriver(type):
    """
    Metaclass for all clusto drivers
    """
    def __init__(cls, name, bases, dct):

        if not hasattr(cls, 'drivername'):
            raise DriverException("Driver %s missing drivername attribute"
                                  % cls.__name__)

        tempattrs = []
        for klass in bases:
            if hasattr(klass, 'meta_attrs'):
                tempattrs.extend(klass.meta_attrs)

        tempattrs.extend(cls.meta_attrs)
        cls.all_meta_attrs = tuple(tempattrs)
        
        if cls.drivername in DRIVERLIST:
            raise KeyError("%s trying to add '%s' to driver list but is "
                           "already claimed by %s."
                           % (cls.__name__,
                              cls.drivername,
                              DRIVERLIST[cls.drivername].__name__))
        
        DRIVERLIST[cls.drivername] = cls

        super(ClustoDriver, cls).__init__(name, bases, dct)

MIXINSFORLIST = {}



class Driver(PoolMixin, AttributeListMixin, object):
    """
    Base Driver.
    """
    
    __metaclass__ = ClustoDriver

    meta_attrs = () # a tuple of (key, value) tuples

    _mixins = set()
    
    drivername = "entity"
    
    def __init__(self, name=None, entity=None, *args, **kwargs):

        if entity:
            self.entity = entity
            self._chooseBestDriver()
            
        else:
            self.entity = Entity(name)
            self.entity.driver = self.drivername

            for attr in self.all_meta_attrs:
                self.addItem(attr)

    def __eq__(self, other):

        if isinstance(other, Entity):
            return self.entity == other
        elif isinstance(other, Driver):
            return self.entity == other.entity
        else:
            return False

    def _chooseBestDriver(self):
        """
        Examine the attributes of our entity and set the best driver class and
        mixins.
        """

        self.__class__ = DRIVERLIST[self.entity.driver]
    
        

    name = property(lambda x: x.entity.name,
                    lambda x,y: setattr(x.entity, 'name', y))

# class ClustoDriverMixin(type):

#     def __init__(mixincls, name, bases, dct):
#         """
#         MetaClass for mixins.  Mainly keeps track of mixin class metadata.
#         """

#         for klass in mixincls._mixinFor:
#             klass._mixins.add(mixincls)
            
#         super(ClustoDriverMixin, mixincls).__init__(name, bases, dct)



# class DriverMixin:

#     __metaclass__ = ClustoDriverMixin

#     _mixinFor = tuple()
    
