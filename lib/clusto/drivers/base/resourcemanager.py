
from clusto.drivers.base import Driver
from clusto.exceptions import ResourceTypeException, ResourceNotAvailableException


class ResourceManagerMixin:

    _entityAttrName = None

    _recordAllocations = True
    

    def allocator(self):
	"""return an unused resource from this resource manager"""

	raise NotImplemented("No allocator implemented for %s you must explicitly specify a resource."
			     % self.name)


    def checkType(self, resource):
	"""checks the type of a given resourece

	if the resource is valid return it and optionally convert it to
	another format.  The format it returns has to be compatible with 
	attribute naming 
	"""
        return resource

    def allocate(self, thing, resource=None):
        """allocates a resource element to the given thing.

	resource - is passed as an argument it will be checked 
	           before assignment.  

	refattr - the attribute name on the entity that will refer back
	          this resource manager.

	returns the resource that was either passed in and processed 
	or generated.
        """
	
	if not isinstance(thing, Driver):
	    raise TypeError("thing is not of type Driver")

        if not resource:
            # allocate a new resource
            resource = self.allocator()

	else:
	    resource = self.checkType(resource)

	self.setAttr(resource, thing)
	

	return resource

    def deallocate(self, thing, resource=None):
        """deallocates a resource from the given thing."""

	if resource is None:
	    rlist = self.resources(thing)
	    for res in rlist:
		self.delAttrs(key=str(res), value=thing)

        if resource and self.available(resource):
            attrname = self._driverName
            thing.delAttrs(key=attrname, value=str(resource))

            self.delAttrs(key=str(resource), value=thing)

    def available(self, resource):
        """return True if resource is available, False otherwise.
        """
        if list(self.attrs(str(resource))):
            return False

        return True
            

    def owners(self, resource):
        """return a list of driver objects for the owners of a given resource.
        """

        return [Driver(x.value) for x in self.attrs(str(resource))]
    
    def resources(self, thing):
        """return a list of resources from the resource manager that is
	associated with the given thing.
        """
	
	return [resource.key for resource in self.attrs() 
		if Driver(resource.value) == thing]


class ResourceManager(ResourceManagerMixin, Driver):
    """The ResourceManager driver should be subclassed by a driver that will
    manage a resource such as IP allocation, MAC Address lists, etc.

    This base class just allocates unique integers.
    
    """
    

    _clustoType = "resource"
    _driverName = "resource"

