from clusto.drivers.base import Driver
from clusto.schema import *

from clusto.exceptions import PoolException

from itertools import imap, chain

class Pool(Driver):
    """
    A Pool is used to group Entities into a collection that shares attributes.

    Pools 
    """
    
    _driver_name = "pool"
    _clusto_type = "pool"


    def insert(self, thing):
        """Insert the given Enity or Driver into this Entity.

        Such that:

        >>> A.insert(B)
        >>> (B in A) 
        True

        A given entity can only be in a Pool one time.
        """
        
        d = self.ensure_driver(thing, 
                               "Can only insert an Entity or a Driver. "
                               "Tried to insert %s." % str(type(thing)))

        if d in self:
            raise PoolException("%s is already in pool %s." % (d, self))
        
        self.add_attr("_contains", d, number=True)
        

    def is_parent(self, thing):
        """
        Is this pool the parent of the given entity
        """
        
        d = self.ensure_driver(thing, 
                               "Can only be the parent of a Driver or Entity.")
        
        return self in d.contents()

    @classmethod
    def get_pools(cls, obj, allPools=True):

        d = cls.ensure_driver(obj, "obj must be either an Entity or a Driver.")


        pools = [Driver(a.entity) for a in d.parents()
                 if isinstance(Driver(a.entity), Pool)]

        if allPools:
            for i in pools:
                pools.extend(Pool.get_pools(i, allPools=True))

        return pools
            
        

class WeightedPool(Pool):
    """Weighted Pool

    Just like a pool but allows its contents to have weights using the
    set/getWeight functions.

    The property 'defaultweight' can be set to set a default weight items
    in the pool.
    """

    _driver_name = "weightedpool"

    
    _properties = {'defaultweight': None }

    def setWeight(self, thing, weight):

        if thing not in self:            
            raise LookupError("%s is not in this pool." % thing)

        self.set_attr("weight", number=weight, value=thing)

    def getWeight(self, thing):

        if thing not in self:            
            raise LookupError("%s is not in this pool." % thing)

        thingattr = self.attrs("weight", value=thing)

        if thingattr:
            return thingattr[0].number
        else:
            return self.defaultweight

