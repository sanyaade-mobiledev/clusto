
import clusto
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
	
	clusto.beginTransaction()

	if not isinstance(thing, Driver):
	    raise TypeError("thing is not of type Driver")

        if not resource:
            # allocate a new resource
            resource, numbered = self.allocator()

	else:
	    resource, numbered = self.ensureType(resource, numbered)

	attr = self.addAttr('resource', thing, numbered=numbered, subkey=resource)
	clusto.commit()

	return attr #resource

    def deallocate(self, thing, resource=(), numbered=True):
        """deallocates a resource from the given thing."""

	if resource is ():
	    for res in self.resources(thing):
		self.delAttrs(res.key, value=thing, 
			      numbered=res.number, subkey=res.subkey)

        if resource and not self.available(resource):
	    resource, numbered = self.ensureType(resource, numbered)
	    
            self.delAttrs('resource', thing, numbered=numbered, subkey=resource)

    def available(self, resource, numbered=()):
        """return True if resource is available, False otherwise.
        """

	resource, numbered = self.ensureType(resource, numbered)


        if self.hasAttr('resource', numbered=numbered, subkey=resource):
            return False

        return True
            

    def owners(self, resource, numbered=True):
        """return a list of driver objects for the owners of a given resource.
        """

	resource, numbered = self.ensureType(resource, numbered)

        return [Driver(x.value) for x in self.attrs('resource', 
						    numbered=numbered,
						    subkey=resource)]
    
    def resources(self, thing):
        """return a list of resources from the resource manager that is
	associated with the given thing.
        """
	
	return self.attrs('resource', thing)



    @property
    def count(self):
	"""Return the number of resources used."""

	return self.attrQuery('resource', count=True)
