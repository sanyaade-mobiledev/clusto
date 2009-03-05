
import clusto
from clusto.drivers.base import Driver
from clusto.exceptions import ResourceTypeException, ResourceNotAvailableException, ResourceLockException



class ResourceManager(Driver):
    """The ResourceManager driver should be subclassed by a driver that will
    manage a resource such as IP allocation, MAC Address lists, etc.

    This base class just allocates unique integers.
    
    """
    

    _clustoType = "resource"
    _driverName = "resource"


    _entityAttrName = None

    _recordAllocations = True
    

    def allocator(self):
        """return an unused resource from this resource manager"""

        raise NotImplemented("No allocator implemented for %s you must explicitly specify a resource."
                             % self.name)


    def ensureType(self, resource, numbered=True):
        """checks the type of a given resourece

        if the resource is valid return it and optionally convert it to
        another format.  The format it returns has to be compatible with 
        attribute naming 
        """
        return (resource, numbered)

    def allocate(self, thing, resource=(), numbered=True):
        """allocates a resource element to the given thing.

        resource - is passed as an argument it will be checked 
                   before assignment.  

        refattr - the attribute name on the entity that will refer back
                  this resource manager.

        returns the resource that was either passed in and processed 
        or generated.
        """

        if not self._recordAllocations:
            return None
        
        clusto.beginTransaction()

        if not isinstance(thing, Driver):
            raise TypeError("thing is not of type Driver")

        if not resource:
            # allocate a new resource
            resource, numbered = self.allocator()

        else:
            resource, numbered = self.ensureType(resource, numbered)

        if numbered and self.checkLock(resource, numbered):
            clusto.rollbackTransaction()
            raise ResourceLockException("Resource %s:%s is locked cannot allocate,"
                                        % (str(resource), str(numbered)))

        attr = self.addAttr(self._driverName, thing, numbered=numbered, subkey=resource)
        clusto.commit()

        return attr #resource

    def deallocate(self, thing, resource=(), numbered=True):
        """deallocates a resource from the given thing."""



        if resource is ():                      
            for res in self.resources(thing):
                self.unlockResource(res.subkey, res.number)
                self.deallocate(thing, res.subkey, res.number)

        if resource and not self.available(resource):
            resource, numbered = self.ensureType(resource, numbered)

            if self.checkLock(resource, numbered):
                raise ResourceLockException("Resource %s:%s is locked cannot deallocate,"
                                            % (str(resource), str(numbered)))


            self.delAttrs(self._driverName, thing, numbered=numbered, subkey=resource)

    def available(self, resource, numbered=()):
        """return True if resource is available, False otherwise.
        """

        resource, numbered = self.ensureType(resource, numbered)


        if self.hasAttr(self._driverName, numbered=numbered, subkey=resource):
            return False

        return True
            

    def owners(self, resource, numbered=True):
        """return a list of driver objects for the owners of a given resource.
        """

        resource, numbered = self.ensureType(resource, numbered)

        return [Driver(x.value) for x in self.attrs(self._driverName, 
                                                    numbered=numbered,
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

    def lockResource(self, resource, numbered=()):
        """lock a resource so that it can't be deallocated or multiply allocated"""


        resource, numbered = self.ensureType(resource, numbered)


        res = self.attrs(self._driverName, numbered=numbered, subkey=resource)

        if len(res) == 0:
            raise ResourceException("Unable to lock a resource because it isn't allocated yet.")
        elif len(res) > 1:
            raise ResourceException("Unable to lock a resource that is allocated to more than one entity.")

        
        self.addattr(self._driverName+'lock', numbered=numbered, subkey=resource, value=res[0].value)

    def unlockResource(self, resource, numbered=()):
        """unlock a resource"""

        resource, numbered = self.ensureType(resource, numbered)

        if self.checkLock(resource, numbered):

            self.delattrs(self._driverName+'lock', numbered=numbered, subkey=resource)
        
    def checkLock(self, resource, numbered=()):
        """check if a given resource is locked"""

        resource, numbered = self.ensureType(resource, numbered)

        if self.hasAttr(self._driverName+'lock', numbered=numbered, subkey=resource):
            return True
        else:
            return False
        
