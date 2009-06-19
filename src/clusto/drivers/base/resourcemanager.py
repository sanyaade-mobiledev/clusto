
import clusto
from clusto.drivers.base import Driver
from clusto.exceptions import ResourceTypeException, ResourceNotAvailableException, ResourceLockException, ResourceException



class ResourceManager(Driver):
    """The ResourceManager driver should be subclassed by a driver that will
    manage a resource such as IP allocation, MAC Address lists, etc.

    This base class just allocates unique integers.
    
    """
    

    _clustoType = "resource"
    _driverName = "resource"


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

    def allocate(self, thing, resource=(), number=True):
        """allocates a resource element to the given thing.

        resource - is passed as an argument it will be checked 
                   before assignment.  

        refattr - the attribute name on the entity that will refer back
                  this resource manager.

        returns the resource that was either passed in and processed 
        or generated.
        """

        clusto.beginTransaction()
        try:
            if not isinstance(thing, Driver):
                raise TypeError("thing is not of type Driver")

            if not resource:
                # allocate a new resource
                resource, number = self.allocator()

            else:
                resource, number = self.ensureType(resource, number)
                if not self.available(resource, number):
                    raise ResourceException("Requested resource is not available.")

            if number and self.checkLock(thing, resource, number):
                raise ResourceLockException("Resource %s:%s is locked cannot allocate,"
                                            % (str(resource), str(number)))

            if self._recordAllocations:
                attr = self.addAttr(self._driverName, thing, number=number, subkey=resource)
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
                    self.deallocate(thing, res.subkey, res.number)


            if resource and not self.available(resource, number):
                resource, number = self.ensureType(resource, number)

                if self.checkLock(thing, resource, number):
                    raise ResourceLockException("Resource %s:%s is locked cannot deallocate,"
                                                % (str(resource), str(number)))


                self.delAttrs(self._driverName, thing, number=number, subkey=resource)
        except Exception, x:
            clusto.rollbackTransaction()
            raise x
    def available(self, resource, number=True):
        """return True if resource is available, False otherwise.
        """

        resource, number = self.ensureType(resource, number)


        if self.hasAttr(self._driverName, number=number, subkey=resource):
            return False

        return True
            

    def owners(self, resource, number=True):
        """return a list of driver objects for the owners of a given resource.
        """

        resource, number = self.ensureType(resource, number)

        return [Driver(x.value) for x in self.attrs(self._driverName, 
                                                    number=number,
                                                    subkey=resource)]

    @classmethod
    def resources(cls, thing):
        """return a list of resources from the resource manager that is
        associated with the given thing.

        A resource is a resource attribute in a resource manager.
        """
        
        return [x for x in thing.references(cls._driverName, thing) 
                if isinstance(Driver(x.entity), cls)]



    @property
    def count(self):
        """Return the number of resources used."""

        return self.attrQuery(self._driverName, count=True)

    def lockResource(self, thing, resource, number=True):
        """lock a resource so that it can't be deallocated or multiply allocated"""


        resource, number = self.ensureType(resource, number)

        clusto.beginTransaction()
        try:
            res = self.attrValues(self._driverName, number=number, subkey=resource)

            if len(res) == 0:
                raise ResourceLockException("Unable to lock a resource because it isn't allocated yet.")
            elif not self.available(resource, number) and thing not in res:
                raise ResourceLockException("Unable to lock resource.")


            if self.attrs(self._driverName+'lock', number=number, subkey=resource, value=thing):
                raise ResourceLockException("Lock already exists for (%s,%s)"
                                            % (str(resource), str(number)))
            
            self.addAttr(self._driverName+'lock', number=number, subkey=resource, value=thing)
            clusto.commit()
        except Exception, x:
            clusto.rollbackTransaction()
            raise x
        
    def unlockResource(self, thing, resource, number=True):
        """unlock a resource"""

        resource, number = self.ensureType(resource, number)

        if self.checkLock(thing, resource, number):

            self.delAttrs(self._driverName+'lock', number=number, subkey=resource, value=thing)
        
    def checkLock(self, thing, resource, number=True):
        """check if a given resource is locked"""


        resource, number = self.ensureType(resource, number)

        if self.hasAttr(self._driverName+'lock', number=number, subkey=resource, value=thing):            
            return True
        else:
            return False
        
