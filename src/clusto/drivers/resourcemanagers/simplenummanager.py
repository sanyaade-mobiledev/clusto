import clusto
from clusto.drivers.base import ResourceManager

from clusto.exceptions import ResourceException
from clusto.schema import ATTR_TABLE

class SimpleNumManagerException(ResourceException):
    pass

class SimpleNumManager(ResourceManager):
    """Manage the generation of numbers that can be associated with Entities
    
    """

    _driverName = "simplenummanager"
    _properties = {'maxnum':None,
                   'next':None,
                   }

    _recordAllocations = True
    
    def __init__(self, nameDriverEntity,
                 startingnum=0,
                 maxnum=False,
                 *args, **kwargs):


        super(SimpleNumManager, self).__init__(nameDriverEntity,
                                              *args, **kwargs)
        
        if maxnum:
            self.maxnum = maxnum

        self.next = startingnum


    def allocator(self):

        clusto.flush()
        num = self.next
        
        if self.maxnum and num > self.maxnum:
            raise SimpleNumManagerException("Out of numbers. "
                                            "Max of %d reached." 
                                            % (self.maxnum))
        
        self.next = ATTR_TABLE.c.int_value + 1

        return ('num', num)
