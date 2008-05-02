
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
            raise KeyError("class '%s' is trying to add the driverName '%s' "
                           "to the driver list but that name is already "
                           "claimed by the '%s' class."
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

