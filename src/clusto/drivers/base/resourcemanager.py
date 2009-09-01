
import clusto
from clusto.schema import select, and_, ATTR_TABLE, Attribute, func
from clusto.drivers.base import Driver
from clusto.exceptions import ResourceTypeException, ResourceNotAvailableException, ResourceException



class ResourceManager(Driver):
    """The ResourceManager driver should be subclassed by a driver that will
    manage a resource such as IP allocation, MAC Address lists, etc.

    This base class just allocates unique integers.
    
    """
    

    _clusto_type = "resourcemanager"
    _driverName = "resourcemanager"

    _attrName = "resource"
    _recordAllocations = True
    


        
    def allocator(self):
        """return an unused resource from this resource manager"""

        raise NotImplemented("No allocator implemented for %s you must explicitly specify a resource."
                             % self.name)


    def ensureType(self, resource, number=True):
        """checks the type of a given resourece

        if the resource is valid return it and optionally convert it to
        another format.  The format it returns has to be compatible with 
        attribute naming 
        """
        return (resource, number)

    def additionalAttrs(self, thing, resource, number):
        pass
    
    def allocate(self, thing, resource=(), number=True):
        """allocates a resource element to the given thing.

        resource - is passed as an argument it will be checked 
                   before assignment.  

        refattr - the attribute name on the entity that will refer back
                  this resource manager.

        returns the resource that was either passed in and processed 
        or generated.
        """

        try:
            clusto.beginTransaction()
            if not isinstance(thing, Driver):
                raise TypeError("thing is not of type Driver")

            if resource is ():
                # allocate a new resource
                resource, number = self.allocator()

            else:
                resource, number = self.ensureType(resource, number)
                if not self.available(resource, number):
                    raise ResourceException("Requested resource is not available.")

            if self._recordAllocations:
                if number == True:
                    attr = thing.addAttr(Attribute(self._attrName,
                                                   resource,
                                                   number=select([func.count('*')],
                                                                 and_(ATTR_TABLE.c.key==self._attrName,
                                                                      ATTR_TABLE.c.number!=None,
                                                                      ATTR_TABLE.c.subkey==None,
                                                                      )).as_scalar(), 
                                                   ))
                else:
                    attr = thing.addAttr(self._attrName, resource, number=number)
                    
                clusto.flush()
                n=select(['number'], ATTR_TABLE.c.attr_id==attr.attr_id).as_scalar()

                a=Attribute(self._attrName,
                            self.entity,
                            number=n,
                            subkey='manager',
                            )
                

                a=thing.addAttr(a)
                                          
                self.additionalAttrs(thing, resource, number)
                
            else:
                attr = None
            clusto.commit()
        except Exception, x:
            clusto.rollbackTransaction()
            raise x

        return attr #resource

    def deallocate(self, thing, resource=(), number=True):
        """deallocates a resource from the given thing."""


        clusto.beginTransaction()
        try:
            if resource is ():                      
                for res in self.resources(thing):
                    thing.delAttrs(self._attrName, number=number)

            elif resource and not self.available(resource, number):
                resource, number = self.ensureType(resource, number)

                res = thing.attrs(self._attrName, self, subkey='manager', number=number)
                for a in res: 
                    thing.delAttrs(self._attrName, number=a.number)
                    
            clusto.commit()
        except Exception, x:
            clusto.rollbackTransaction()
            raise x
    def available(self, resource, number=True):
        """return True if resource is available, False otherwise.
        """

        resource, number = self.ensureType(resource, number)

        if self.owners(resource, number):
            return False

        return True
            

    def owners(self, resource, number=True):
        """return a list of driver objects for the owners of a given resource.
        """

        resource, number = self.ensureType(resource, number)

        return Driver.getByAttr(self._attrName, resource, number=number)

    @classmethod
    def resources(cls, thing):
        """return a list of resources from the resource manager that is
        associated with the given thing.

        A resource is a resource attribute in a resource manager.
        """
        
        attrs = [x for x in thing.attrs(cls._attrName, subkey='manager') 
                 if isinstance(Driver(x.value), cls)]

        res = []

        for attr in attrs:
            t=thing.attrs(cls._attrName, number=attr.number, subkey=None)
            res.extend(t)


        return res

    @property
    def count(self):
        """Return the number of resources used."""

        return len(self.references(self._attrName, self, subkey='manager'))

    def getResourceNum(self, thing, resource):
        """Retrun the resource number for the given resource on the given Entity"""

        resource, number = self.ensureType(resource)
        res = thing.attrs(self._attrName, number=number, value=resource)

        if res:
            return res[0].number
        else:
            return None

        
    def getResourceAttrs(self, thing, resource):
        """Return the Attribute objects for a given resource on a given Entity"""
        
        resource, number = self.ensureType(resource)

        return thing.attrs(self._attrName, number=number, value=resource)
