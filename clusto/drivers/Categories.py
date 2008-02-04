from clusto.drivers.Base import Driver


class Pool(Driver):
    """
    A Pool is used to group Entities into a collection that shares attributes.

    Pools 
    """
    
    drivername = "pool"

    def addToPool(self, entity):
        """
        Add a given Entity to the pool.

        @param entity: the entity to be added
        @type entity: L{Entity} or L{Driver}
        """

            
        self.addAttr('_member', entity)
        entity.addAttr('_inPool', self)


    def removeFromPool(self, entity):
        """
        remove a given Entity from the pool.

        @param entity: the entity to be removed
        @type entity: L{Entity} or L{Driver}
        """

        self.delAttr('_member', entity)
        entity.delAttr('_inPool', self)
        
    @property
    def members(self):
        """
        Return a list of members in th pool
        """

        return [x.value for x in self.getAttr('_member', all=True)]

        
