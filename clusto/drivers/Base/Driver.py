
import re
import itertools

from clusto.schema import *
from clusto.exceptions import *

from ClustoDriver import *


class Driver(object):
    """
    Base Driver.
    """
    
    __metaclass__ = ClustoDriver

    meta_attrs = () # a tuple of (key, value) tuples

    _mixins = set()
    
    _type = "generic"
    _driverName = "entity"
    _reservedAttrs = tuple()

    _properties = tuple()
    
    def __init__(self, name=None, entity=None, *args, **kwargs):

        if entity:
            self.entity = entity
            self._chooseBestDriver()
            
        else:
            self.entity = Entity(name)
            self.entity.driver = self._driverName
            self.entity.type = self._type

            #for attr in self.all_meta_attrs:
            #    self.addItem(attr)

        
    def __eq__(self, other):

        if isinstance(other, Entity):
            return self.entity.name == other.name
        elif isinstance(other, Driver):
            return self.entity.name == other.entity.name
        else:
            return False

    def __cmp__(self, other):

        return cmp(self.name, other.name)


    def __contains__(self, other):
        return False
    
    def _chooseBestDriver(self):
        """
        Examine the attributes of our entity and set the best driver class and
        mixins.
        """

        self.__class__ = DRIVERLIST[self.entity.driver]
    
        

    name = property(lambda x: x.entity.name,
                    lambda x,y: setattr(x.entity, 'name', y))


    def _checkAttrName(self, key):
        """
        check to make sure the key does not contain invalid characters
        raise NameException if fail.
        """

        if not re.match('^[A-Za-z_]+[0-9A-Za-z_]*(-[A-Za-z]+[0-9A-Za-z_-]*)?$', key):

            raise NameException("Attribute name %s is invalid. "
                                "Attribute names may not contain periods or "
                                "comas." % key)
    
        
    def _buildKeyName(self, key, numbered=None, subkey=None):

        keyname = key
        if numbered is not None:
            if isinstance(numbered, bool):
                number = self._getAttrNumCount(key, numbered=numbered)
            elif isinstance(numbered, int):
                number = numbered
            else:
                raise TypeError("num must be either True, or an integer.")

            keyname += str(number)

        if subkey: 
            keyname += ''.join(['-', str(subkey)])

        self._checkAttrName(keyname)

        return keyname

    def _getAttrNumCount(self, key, numbered=None):
        """
        For numbered attributes return the count that exist
        """
        attrs = self.attrs(key=key, numbered=numbered)

        return len(list(attrs))
        
    def attrs(self, key=None, value=None, numbered=None, subkey=None,
              ignoreHidden=True, strict=False, mergedPoolAttrs=False,
              overrideParent=True, sortByKeys=True
              ):
        """
        Function to get and filter the attributes of an entity in many
        different ways.

        
        """

        #if ignoreHidden:
        #    all = filter(lambda x: not x.key.startswith('_'), all)

        regex = ["^"]

        if key and key.startswith('_'):
            ignoreHidden=False
            
        if ignoreHidden:
            regex.append("(?!_)")
            
        regex.append((key and key or ".*"))

        if isinstance(numbered, bool):
            regex.append("\d+")
        elif isinstance(numbered, int):
            regex.append(str(numbered))

        if isinstance(subkey, str):
            regex.append("-%s" % subkey)
        elif subkey is True:
            regex.append("-.+")

        if strict:
            regex.append("$")

        vals = (x for x in self.entity._attrs if re.match(''.join(regex), x.key))
        if value:
            vals = (x for x in vals if x.value == value)

        if not mergedPoolAttrs:
            allattrs = vals
        else:
            allattrs = itertools.chain(vals,
                                       *(i.attrs(key=key,
                                                 value=value,
                                                 numbered=numbered,
                                                 subkey=subkey,
                                                 ignoreHidden=ignoreHidden,
                                                 strict=strict,
                                                 mergedPoolAttrs=mergedPoolAttrs)
                                         for i in self.iterPools()))

            if overrideParent:
                # FIXME
                # I don't think this will really do what I want.
                def doOverride(attrs):
                    skipAttrs = set()

                    for i in attrs:
                        if i.key in skipAttrs:
                            continue
                        yield i
                        skipAttrs.add(i.key)
                        
                allattrs = doOverride(allattrs)

    
        if not allattrs:
            return None

        if sortByKeys:
            return sorted(allattrs)
        
        return allattrs



    def attrKeys(self, *args, **kwargs):

        return (x.key for x in self.attrs(*args, **kwargs))

    def attrItems(self, *args, **kwargs):
        return ((x.key, x.value) for x in self.attrs(*args, **kwargs))

    def addAttr(self, key, value, numbered=None, subkey=None):
        """
        add a key/value to the list of attributes

        if numbered is True, append the next available int to the key name.
        if numbered is an int, append that int to the key name
        if subkey is specified append '_subkey' to the key name
         subkeys don't get numbered
        """

        keyname = self._buildKeyName(key, numbered, subkey)
        self.entity._attrs.append(Attribute(keyname, value))

    def delAttrs(self, *args, **kwargs):
        "delete attribute with the given key and value optionally value also"


        for i in self.attrs(*args, **kwargs):
            self.entity._attrs.remove(i)
            i.delete()

    def setAttr(self, key, valuelist):
        """
        replaces all items in the list matching the given key with values in
        valuelist
        """
        self._checkAttrName(key)
        self.delAttrs(key=key)
        for val in valuelist:
            self.addAttr(key, val)

    
    def hasAttr(self, strict=True, *args, **kwargs):
        "return True if this list has an attribute with the given key"

        for i in self.attrs(strict=strict, *args, **kwargs):
            return True

        return False
    
    def iterPools(self, allPools=True):
        """
        Return an iterator that iterates over the pools that a given entity is
        a member of.

        The first pool returned is the most recently added pool in a
        breadthfirst manner.

        So, say I have an entity that was added to pools A, B, C in that order
        and pool A is in pools (A1, B2), pool B is in (B1, A1), pool C is in
        (C1).  Then the returned values will be:

            C, B, A, C1, A1, B1, B2, A1

        In this way the attributes of more recent pools can override the
        attributes of older pools.
        """

        def poolGenerator(entity):


            pools = [Driver(entity=x.value)
                     for x in sorted(entity.attrs('_inPool',
                                                  numbered=True),
                                     cmp=lambda x,y: cmp(x.key, y.key),
                                     reverse=True)]
            
            while pools:
                pool = pools.pop(0)
                yield pool

                if allPools:
                    pools.extend(list(poolGenerator(pool)))
                            

        return poolGenerator(self)


    def insert(self, thing):

        if isinstance(thing, Entity):
            pass
            

