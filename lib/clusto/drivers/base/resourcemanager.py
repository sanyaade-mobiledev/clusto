
from clusto.drivers.base import Driver
from clusto.exceptions import ResourceTypeException, ResourceNotAvailableException



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


    def ensureType(self, resource, numbered=True, subkey=None):
	"""checks the type of a given resourece

	if the resource is valid return it and optionally convert it to
	another format.  The format it returns has to be compatible with 
	attribute naming 
	"""
        return (resource, numbered, subkey)

    def allocate(self, thing, resource=None, numbered=True, subkey=None):
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
            resource, numbered, subkey = self.allocator()

	else:
	    resource, numbered, subkey = self.ensureType(resource, 
							numbered, 
							subkey)

	self.setAttr(resource, thing, numbered=numbered, subkey=subkey)
	

	return resource

    def deallocate(self, thing, resource=None, numbered=True, subkey=None):
        """deallocates a resource from the given thing."""

	if resource is None:
	    for res in self.resources(thing):
		self.delAttrs(res.key, value=thing, 
			      numbered=res.number, subkey=res.subkey)

        if resource and not self.available(resource):
	    resource, numbered, subkey = self._ensureType(resource, numbered, subkey)
	    
            self.delAttrs(resource, thing, numbered=numbered, subkey=subkey)

    def available(self, resource, numbered=None, subkey=None):
        """return True if resource is available, False otherwise.
        """

	resource, numbered, subkey = self._ensureType(resource, numbered, subkey)

        if self.attrs(resource, numbered=numbered, subkey=subkey):
            return False

        return True
            

    def owners(self, resource, numbered=True, subkey=None):
        """return a list of driver objects for the owners of a given resource.
        """


	resource, number, subkey = self._ensureType(resource, number, subkey)

        return [Driver(x.value) for x in self.attrs(resource, 
						    numbered=numbered,
						    subkey=subkey)]
    
    def resources(self, thing):
        """return a list of resources from the resource manager that is
	associated with the given thing.
        """
	
	return [resource for resource in self.attrs() 
		if Driver(resource.value) == thing]


