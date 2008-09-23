
import re
import itertools

import clusto
from clusto.schema import *
from clusto.exceptions import *

from clustodriver import *


class Driver(object):
    """
    Base Driver.
    """
    
    __metaclass__ = ClustoDriver

    meta_attrs = () # a tuple of (key, value) tuples

    _mixins = set()
    
    _clustoType = "generic"
    _driverName = "entity"
    _reservedAttrs = tuple()

    _properties = dict()
    #_defaultAttrs = tuple()

    def __new__(cls, nameDriverEntity, **kwargs):

	if isinstance(nameDriverEntity, Driver):
	    return nameDriverEntity
	else:
	    return object.__new__(cls, nameDriverEntity, **kwargs)

    def __init__(self, nameDriverEntity, **kwargs):

        if not isinstance(nameDriverEntity, (str, unicode, Entity, Driver)):
            raise TypeError("First argument must be a string, "
                            "Driver, or Entity.")

	if isinstance(nameDriverEntity, Driver):
	    return 

        if isinstance(nameDriverEntity, Entity):
            
            self.entity = nameDriverEntity
            self._chooseBestDriver()

        elif isinstance(nameDriverEntity, (str, unicode)):
            
            self.entity = Entity(nameDriverEntity)
            self.entity.driver = self._driverName
            self.entity.type = self._clustoType

        else:
            raise TypeError("Could not create driver from given arguments.")

        for key, val in kwargs.iteritems():
            if key in self._properties:
                setattr(self, key, val)
            ## unsure if I should fail on bad keys

        
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
        return self.hasAttr(key="_contains", value=other)
    
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

        if not isinstance(key, basestring):
            raise TypeError("An attribute name must be a string.")

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

    def _buildKeyRegex(self, key=None, value=None, numbered=None,
                    subkey=None, ignoreHidden=True, strict=False):
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

            return regex

    def _attrQuery(self, key=None, value=None, numbered=None,
		   subkey=None, ignoreHidden=True, 
		   mergedPoolAttrs=False, overrideParent=True,
		   sortByKeys=True, 
		   glob=True, allattrs=False
		   ):

	
	querydict = {}

	query = SESSION.query(Attribute)

	if not allattrs:
	    query = query.filter_by(entity_id=self.entity_id)

	if key is not None:
	    if glob:
		query = query.filter(Attribute.key_name.like(key.replace('*', '%')))
	    else:
		querydict['key_name'] = key

	if subkey is not None:
	    if glob:
		query = query.filter(Attribute.key_name.like(subkey.replace('*', '%')))
	    else:
		querydict['subkey_name'] = subkey

	if value is not None:
	    typename = Attribute.getType(value)

	    if typename == 'relation':
		querydict['relation_id'] = value

	if numbered is not None:
	    if isinstance(numbered, bool):
		if numbered == True:
		    query.filter(key_number != None)
		else:
		    query.filter(key_number == None)
	    elif isinstance(numbered, int):
		querydict['key_number'] = numbered
		

	    else:
		raise TypeError("num must be either a boolean or an integer.")

	if ignoreHidden:
	    query.filter(not_(Attribute.key_name.like('_%')))

	for k, v in querydict.iteritems():
	    if v == '':
		querydict[k] = None

	query = query.filter_by(*querydict)

	return query.all()
		   
    def _attrFilter(self, attrlist, key=None, value=None, numbered=None,
                    subkey=None, ignoreHidden=True, strict=False,
                    mergedPoolAttrs=False, overrideParent=True,
                    sortByKeys=True, parentType=None, parentDriver=None,
                    regex=None
                    ):
        """
        This function lets you sort through various kinds of attribute lists.
        """

        if not regex:
            regex = self._buildKeyRegex(key=key, value=value,
                                        numbered=numbered,
                                        subkey=subkey,
                                        ignoreHidden=ignoreHidden,
                                        strict=strict)
            
        vals = (x for x in attrlist if re.match(''.join(regex), x.key))
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


        return list(allattrs)

        
    def attrs(self, *args, **kwargs):
        """
        Function to get and filter the attributes of an entity in many
        different ways.

        
        """
        return self._attrFilter(self.entity._attrs, *args, **kwargs)

    def references(self, *args, **kwargs):

        clustotype = None
        if 'clustotype' in kwargs:
            clustotype = kwargs['clustotype']
            kwargs.pop('clustotype')
            
        attrs = self._attrFilter(self.entity._references, *args, **kwargs)

        if clustotype:
            attrs = (x for x in attrs
                     if x.entity.type == clustotype)

        return list(attrs)
                   
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

        if isinstance(value, Driver):
            self.entity._attrs.append(Attribute(keyname, value.entity))
        else:
            self.entity._attrs.append(Attribute(keyname, value))

    def delAttrs(self, *args, **kwargs):
        "delete attribute with the given key and value optionally value also"


        for i in self.attrs(*args, **kwargs):
            self.entity._attrs.remove(i)
            i.delete()

    def setAttr(self, key, value, numbered=None, subkey=None):
        """replaces all items in the list matching the given key with value
        """
        self._checkAttrName(key)
        self.delAttrs(key=key, numbered=numbered, subkey=subkey)
	self.addAttr(key, value, numbered=numbered, subkey=subkey)
	

    
    def hasAttr(self, *args, **kwargs):
        """return True if this list has an attribute with the given key"""

        if 'strict' not in kwargs:
            kwargs['strict'] = True
        for i in self.attrs(*args, **kwargs):
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


            pools = [Driver(x.entity)
                     for x in sorted(entity.references('_member',
                                                       numbered=True),
                                     cmp=lambda x,y: cmp(x.attr_id, y.attr_id),
                                     reverse=True)]
            
            while pools:
                pool = pools.pop(0)
                yield pool

                if allPools:
                    pools.extend(list(poolGenerator(pool)))
                            

        return poolGenerator(self)


    def insert(self, thing):
        """
        Insert the given Enity or Driver into this Entity.  Such that:

            A.insert(B)

            (B in A) == True


        """
        if isinstance(thing, Entity):
            d = Driver(Entity)
        elif isinstance(thing, Driver):
            d = thing
        else:
            raise TypeError("Can only insert an Entity or a Driver. "
                            "Tried to insert %s." % str(type(thing)))

        self.addAttr("_contains", d)
        

    @classmethod
    def getByAttr(self, attrname, value):
        """
        Return a list of Instances that have the given attribute with the given
        value.
        """


        querydict = { Attribute.getType(value)+"_value": value}
        querydict.update(Attribute.splitKeyName(attrname))
                     
        attrlist = SESSION.query(Attribute).filter_by(**querydict)


        objs = [Driver(x.entity) for x in attrlist]

        return objs
            
