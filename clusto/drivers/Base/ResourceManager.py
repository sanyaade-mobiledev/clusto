
from clusto.drivers.Base import Driver
from clusto.exceptions import ResourceTypeException, ResourceNotAvailableException

class ResourceManager(Driver):
    """
    The ResourceManager driver should be subclassed by a driver that will
    manage a resource such as IP allocation, MAC Address lists, etc.

    This base class just allocates unique integers.
    
    """
    

    _clustotype = "resource"
    _driverName = "resource"

    _entityAttrName = None

    def allocator(self):
        return None

    def checkType(self, resource):
        return True

    def allocate(self, thing, resource=None):
        """
        allocates a resource element to the given thing.
        """

        if not resource:
            # allocate a new resource
            resource = self.allocator()
        elif not self.checkType(resource):
            raise ResourceTypeException("The resource %s you're trying to "
                                        "allocate is of the wrong type."
                                        % str(resource))
        elif not self.available(resource):
            raise ResourceNotAvailableException("Resource %s is not available."
                                                % str(resource))
            


        # make the resource an attribute of the entity if necessary
        if self._entityAttrName:
            thing.addAttr(self._entityAttrName, resource, numbered=True)

        self.addAttr(str(resource), thing)
            

    def deallocate(self, thing, resource=None):
        """
        deallocates a resource from the given thing.
        """

        if not resource:
            # TODO
            # deallocate all managed resources from given thing
            pass

        for i in resources:
            attrname = self._driverName
            thing.delAttr(attrname, i)

            self.delAttr(str(i))

    def available(self, resource):
        """
        return True if resource is available, False otherwise.
        """
        if list(self.attrs(str(resource))):
            return False

        return True
            

    def owner(self, resource):
        """
        return the owner object of a given resource.
        """

        return self.attrs(str(resource))
    
