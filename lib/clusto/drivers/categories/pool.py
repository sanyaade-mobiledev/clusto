from clusto.drivers.base import Driver
from clusto.schema import *

from itertools import imap, chain

class Pool(Driver):
    """
    A Pool is used to group Entities into a collection that shares attributes.

    Pools 
    """
    
    _driverName = "pool"
    _clustoType = "pool"
    
    def isParent(self, thing):
        """
        Is this pool the parent of the given entity
        """
	
	if isinstance(thing, Entity):
	    d = Driver(Entity)
        elif isinstance(thing, Driver):
            d = thing
        else:
            raise TypeError("Can only remove an Entity or a Driver. "
                            "Tried to remove %s." % str(type(thing)))

	
	return self in d.contents()

    @classmethod
    def getPools(cls, obj, allPools=False):

        if isinstance(obj, Driver):
            pass           
        elif isinstance(obj, Entity):
            obj = Driver(entity=entity)
        else:
            raise TypeError("obj must be either an Entity or a Driver.")


        q = SESSION.query(Attribute).filter(and_(Entity.driver==cls._driverName,
                                                 Entity.entity_id==Attribute.entity_id,
                                                 Attribute.relation_value==obj.entity,
                                                 Attribute.key_name=='_member'
                                                 ))

        
        pools = set([Driver(x.entity) for x in q])

        if allPools:
            for i in list(pools):
                pools.update(Pool.getPools(i, allPools=True))

        return pools
            
        
