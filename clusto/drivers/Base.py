from clusto.schema import *
from clusto.exceptions import *
import clusto
from clusto.drivers.Mixins import *

DRIVERLIST = {}
RESERVEDATTRS = {}

class ClustoDriver(type):
    """
    Metaclass for all clusto drivers
    """
    def __init__(cls, name, bases, dct):

        if not hasattr(cls, '_driverName'):
            raise DriverException("Driver %s missing _driverName attribute"
                                  % cls.__name__)

        if not hasattr(cls, '_reservedAttrs'):
            raise DriverException("Driver %s missing _reservedAttrs attribute"
                                  % cls.__name__)

        tempattrs = []
        for klass in bases:
            if hasattr(klass, 'meta_attrs'):
                tempattrs.extend(klass.meta_attrs)

        tempattrs.extend(cls.meta_attrs)
        cls.all_meta_attrs = tuple(tempattrs)
        
        if cls._driverName in DRIVERLIST:
            raise KeyError("%s trying to add '%s' to driver list but is "
                           "already claimed by %s."
                           % (cls.__name__,
                              cls._driverName,
                              DRIVERLIST[cls._driverName].__name__))
        


        for i in cls._reservedAttrs:
            if i in RESERVEDATTRS:
                raise DriverException("Driver %s is attempting to reserve "
                                      "attribute %s which is already reserved "
                                      "by driver %s"
                                      % (cls.__name__,
                                         i,
                                         RESERVEDATTRS[i].__name__))
            RESERVEDATTRS[i] = cls
        
            
        DRIVERLIST[cls._driverName] = cls


        # setup properties
        for i in cls._properties:

            def getter(self, key=i):
                attr = self.getAttr(key)
                if not attr:
                    return None
                else:
                    return attr.value
            def setter(self, val, key=i):
                self.setAttr(key, (val,))


            setattr(cls, i, property(getter, setter))



        super(ClustoDriver, cls).__init__(name, bases, dct)

MIXINSFORLIST = {}



class Driver(PoolMixin, AttributeListMixin, object):
    """
    Base Driver.
    """
    
    __metaclass__ = ClustoDriver

    meta_attrs = () # a tuple of (key, value) tuples

    _mixins = set()
    
    _driverName = "entity"
    _reservedAttrs = tuple()

    _properties = tuple()
    
    def __init__(self, name=None, entity=None, *args, **kwargs):

        if entity:
            self.entity = entity
            self._chooseBestDriver()
            
        else:
            self.entity = Entity(name)
            self.entity.driver = self._driverName

            #for attr in self.all_meta_attrs:
            #    self.addItem(attr)

        
    def __eq__(self, other):

        if isinstance(other, Entity):
            return self.entity.name == other.name
        elif isinstance(other, Driver):
            return self.entity.name == other.entity.name
        else:
            return False

    def __cmp__(self, other):

        return cmp(self.name, other.name)
    
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
    
