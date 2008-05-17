from clusto.drivers.Base import ResourceManager

from clusto.exceptions import ResourceException

class SimpleNameManagerException(ResourceException):
    pass

class SimpleNameManager(ResourceManager):
    """
    SimpleNameManager - manage the generation of a names with a common
    prefix and an incrementing integer component.

    e.g foo001, foo002, foo003, etc.
    
    """

    _driverName = "simplenamemanager"
    _properties = ('basename', 'digits', 'next', 'leadingZeros')

    _recordAllocations = False
    
    def __init__(self, name=None, entity=None,
                 basename='',
                 digits=2,
                 startingnum=1,
                 incrementForever=True,
                 leadingZeros=True,
                 *args, **kwargs):


        super(ResourceManager, self).__init__(name=name, entity=entity,
                                              *args, **kwargs)
        
        self.basename = basename
        self.digits = digits
        self.next = startingnum
        self.leadingZeros = leadingZeros

    def allocator(self):

        num = str(self.next)

        if self.leadingZeros:
            num = num.rjust(self.digits, '0')

        if len(num) > self.digits:
            raise SimpleNameManagerException("Out of digits for the integer. "
                                             "Max of %d digits and we're at "
                                             "number %s." % (self.digits, num))
        nextname = self.basename + num
        self.next += 1
        return nextname
        
    
    def createEntity(self, clustotype, *args, **kwargs):
        """
        Create an entity with a name generated from this NameResource
        """

        name = self.allocator()

        newobj = clustotype(name=name, *args, **kwargs)

        self.allocate(newobj, name)

        return newobj


