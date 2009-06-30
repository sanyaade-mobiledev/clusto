import clusto
from clusto.drivers.base import ResourceManager

from clusto.exceptions import ResourceException
from clusto.schema import ATTR_TABLE

class SimpleNameManagerException(ResourceException):
    pass

class SimpleNameManager(ResourceManager):
    """
    SimpleNameManager - manage the generation of a names with a common
    prefix and an incrementing integer component.

    e.g foo001, foo002, foo003, etc.
    
    """

    _driverName = "simplenamemanager"
    _properties = {'basename':'',
                   'digits':2,
                   'next':1,
                   'leadingZeros':int(True)}

    _recordAllocations = True
    
    def allocator(self):
        clusto.flush()
        num = str(self.next)

        if self.leadingZeros:
            num = num.rjust(self.digits, '0')

        if len(num) > self.digits:
            raise SimpleNameManagerException("Out of digits for the integer. "
                                             "Max of %d digits and we're at "
                                             "number %s." % (self.digits, num))
        
        nextname = self.basename + num

        self.next = ATTR_TABLE.c.int_value + 1

        return (nextname, None)
        

class SimpleEntityNameManager(SimpleNameManager):    

    _driverName = "simpleentitynamemanager"

    _recordAllocations = False


    def allocate(self, clustotype, resource=None, number=True):
        """allocates a resource element to the given thing.

        resource - is passed as an argument it will be checked 
                   before assignment.  

        refattr - the attribute name on the entity that will refer back
                  this resource manager.

        returns the resource that was either passed in and processed 
        or generated.
        """

        if not isinstance(clustotype, type):
            raise TypeError("thing is not a Driver class")

        clusto.beginTransaction()

        if not resource:
            name, num = self.allocator()

            newobj = clustotype(name)

        else:
            name = resource
            newobj = clustotype(resource)


        super(SimpleEntityNameManager, self).allocate(newobj, name)

        clusto.commit()

        return newobj


    def deallocate(self, thing, resource=None, number=True):
        raise Exception("can't deallocate an entity name, delete the entity instead.")

