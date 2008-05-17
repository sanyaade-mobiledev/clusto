from clusto.drivers.Base import Driver
from clusto.schema import *

from itertools import imap, chain

class Pool(Driver):
    """
    A Pool is used to group Entities into a collection that shares attributes.

    Pools 
    """
    
    _driverName = "pool"
    _clustoType = "pool"
    

    def addToPool(self, entity):
        """
        Add a given Entity to this pool.

        @param entity: the entity to be added
        @type entity: L{Entity} or L{Driver}
        """


        self.addAttr('_member', entity, numbered=True)
        #entity.addAttr('_inPool', self, numbered=True)


    def removeFromPool(self, entity):
        """
        remove a given Entity from the pool.

        @param entity: the entity to be removed
        @type entity: L{Entity} or L{Driver}
        """

        self.delAttr('_member', entity, numbered=True)
        #entity.delAttr('_inPool', self)
        
    @property
    def members(self):
        """
        Return a list of members in th pool
        """

        return [x.value for x in self.attrs(key='_member',
                                            numbered=True,
                                            ignoreHidden=False)]


    def isParent(self, entity):
        """
        Is this pool the parent of the given entity
        """

        pass

    @classmethod
    def getPools(cls, obj, allPools=False):

        if isinstance(obj, Driver):
            pass           
        elif isinstance(obj, Entity):
            obj = Driver(entity=entity)
        else:
            raise TypeError("obj must be either an Entity or a Driver.")


        q = SESSION.query(Attribute).filter(and_(Entity.c.driver==cls._driverName,
                                                 Entity.c.entity_id==Attribute.c.entity_id,
                                                 Attribute.relation_value==obj.entity,
                                                 Attribute.c.key.like('_member%')
                                                 ))

        
        pools = set([Driver(entity=x.entity) for x in q])

        if allPools:
            for i in list(pools):
                pools.update(Pool.getPools(i, allPools=True))

        return pools
            
        
