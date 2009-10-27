
import clusto
from clusto.schema import select, and_, ATTR_TABLE, Attribute, func, Counter
from clusto.drivers.base import Driver, ClustoMeta
from clusto.exceptions import ResourceTypeException, ResourceNotAvailableException, ResourceException



class ResourceManager(Driver):
    """The ResourceManager driver should be subclassed by a driver that will
    manage a resource such as IP allocation, MAC Address lists, etc.

    This base class just allocates unique integers.
    
    """
    

    _clusto_type = "resourcemanager"
    _driver_name = "resourcemanager"

    _attr_name = "resource"
    _record_allocations = True
    


        
    def allocator(self):
        """return an unused resource from this resource manager"""

        raise NotImplemented("No allocator implemented for %s you must explicitly specify a resource."
                             % self.name)


    def ensure_type(self, resource, number=True):
        """checks the type of a given resourece

        if the resource is valid return it and optionally convert it to
        another format.  The format it returns has to be compatible with 
        attribute naming 
        """
        return (resource, number)

    def additional_attrs(self, thing, resource, number):
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
            clusto.begin_transaction()
            if not isinstance(thing, Driver):
                raise TypeError("thing is not of type Driver")

            if resource is ():
                # allocate a new resource
                resource, number = self.allocator()

            else:
                resource, number = self.ensure_type(resource, number)
                if not self.available(resource, number):
                    raise ResourceException("Requested resource is not available.")

            if self._record_allocations:
                if number == True:

                    c = Counter.get(ClustoMeta().entity, self._attr_name)
                    attr = thing.add_attr(self._attr_name,
                                          resource,
                                          number=c
                                          )

                else:
                    attr = thing.add_attr(self._attr_name, resource, number=number)
                    
                clusto.flush()

                a=thing.add_attr(self._attr_name,
                            self.entity,
                            number=attr.number,
                            subkey='manager',
                            )
                                          
                self.additional_attrs(thing, resource, number)
                
            else:
                attr = None
            clusto.commit()
        except Exception, x:
            clusto.rollback_transaction()
            raise x

        return attr #resource

    def deallocate(self, thing, resource=(), number=True):
        """deallocates a resource from the given thing."""


        clusto.begin_transaction()
        try:
            if resource is ():                      
                for res in self.resources(thing):
                    thing.del_attrs(self._attr_name, number=number)

            elif resource and not self.available(resource, number):
                resource, number = self.ensure_type(resource, number)

                res = thing.attrs(self._attr_name, self, subkey='manager', number=number)
                for a in res: 
                    thing.del_attrs(self._attr_name, number=a.number)
                    
            clusto.commit()
        except Exception, x:
            clusto.rollback_transaction()
            raise x
    def available(self, resource, number=True):
        """return True if resource is available, False otherwise.
        """

        resource, number = self.ensure_type(resource, number)

        if self.owners(resource, number):
            return False

        return True
            

    def owners(self, resource, number=True):
        """return a list of driver objects for the owners of a given resource.
        """

        resource, number = self.ensure_type(resource, number)

        return Driver.get_by_attr(self._attr_name, resource, number=number)

    @classmethod
    def resources(cls, thing):
        """return a list of resources from the resource manager that is
        associated with the given thing.

        A resource is a resource attribute in a resource manager.
        """
        
        attrs = [x for x in thing.attrs(cls._attr_name, subkey='manager') 
                 if isinstance(Driver(x.value), cls)]

        res = []

        for attr in attrs:
            t=thing.attrs(cls._attr_name, number=attr.number, subkey=None)
            res.extend(t)


        return res

    @property
    def count(self):
        """Return the number of resources used."""

        return len(self.references(self._attr_name, self, subkey='manager'))

    def get_resource_number(self, thing, resource):
        """Retrun the resource number for the given resource on the given Entity"""

        resource, number = self.ensure_type(resource)
        res = thing.attrs(self._attr_name, number=number, value=resource)

        if res:
            return res[0].number
        else:
            return None

        
    def get_resource_attrs(self, thing, resource):
        """Return the Attribute objects for a given resource on a given Entity"""
        
        resource, number = self.ensure_type(resource)

        return thing.attrs(self._attr_name, number=number, value=resource)
