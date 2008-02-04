
from clusto.schema import Attribute


class AttributeListMixin:
    """
    Methods that provides functionality for working with attribute lists.
    """

    def addAttr(self, key, value):
        "add a key/value to the list of attributes"

        self.entity._attrs.append(Attribute(key, value))

    def delAttr(self, key, value=None):
        "delete attribute with the given key and value optionally value also"

        for i in sef.entity._attrs:
            if value:
                if (i.key == key) and (i.value == value):
                    i.delete()
            else:
                if (i.key == key):
                    i.delete()

    @property
    def attrs(self):
        return tuple(self.entity._attrs)

    def attrKeys(self):

        return [x.key for x in self.attrs]
        
    def getAttr(self, key, all=False):
        "get all values for a given key"

        vals = filter(lambda x: x.key == key, self.attrs)
        return all and tuple(vals) or vals[0]

    def setAttr(self, key, valuelist):
        """
        replaces all items in the list matching the given key with values in
        valuelist
        """

        self.delAttr(key)
        for val in valuelist:
            self.addAttr(Attribute(key, val))

    
    def hasAttr(self, key):
        "return True if this list has an attribute with the given key"

        for i in self.attrs:
            if i.key == key:
                return True

        return False
    


class PoolMixin:
    """
    mixin so Entities can interact with pools they are in
    """

    def attrs(self, ignoreHidden=True, onlyLocal=False, attrfilter=None):

        all = list(self.entity._attrs)

        if ignoreHidden:
            all = filter(lambda x: not x.key.startswith('_'), all)

        if not onlyLocal:
            for pool in self.pools():
                all.extend(pool.attrs())

        if filter:
            all = filter(attrfilter, all)
            
        return all
    


    def getAttr(self, key, all=False, onlyLocal=False):
        "get all values for a given key"


        attrs = self.attrs(ignoreHidden=False, onlyLocal=onlyLocal)
        
        vals = filter(lambda x: x.key == key, attrs)
        
        return all and tuple(vals) or (vals and vals[0] or [])


    
    def pools(self):

        pools = [self.__class__(entity=x.value) for x in self.getAttr('_inPool', all=True, onlyLocal=True)]

        return pools


    def removeFromPools(self):
        "Remove this Entity from all pools"

        for pool in self.pools:
            pool.removeFromPool(self)

        

