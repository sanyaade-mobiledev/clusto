"""Driver class

A Driver provides an interface to an Entity and its Attributes.
"""

import re
import itertools

import clusto
from clusto.schema import *
from clusto.exceptions import *

from clustodriver import *


class Driver(object):
    """Base Driver.

    The Driver class provides a proxy interface for managing and Entity and
    its Attributes. It provides many helper functions includeing attribute
    setters and accessors, attribute querying, and a handful of conventions.

    Every driver defines a _clustoType and a _driverName member variable.
    Upon creation these become the type and driver for the Entity and provides
    a mechanism for choosing the correct driver for a given Entity.

    A Driver can be created by passing either the name (a string) for a new
    Entity you'd like to create, an already instantiated Entity object, or a
    Driver object (which has already been instantiated and is managing an
    Entity).

    If a _properties member dictionary is defined they will be treated as
    default values for the given Entity attributes as well as exposed via a
    simpler mydriver.key access pattern.  So for:

    >>> class MyDriver(Driver):
    >>>    ...
    >>>    _properties = {'propA': 10, 'propB': "default1"}
    >>>    ...

    >>> d = MyDriver('foo')
    >>> d.propA == 10
    True
    
    >>> d.propB == "default1"
    True

    Only properties with non-None default values are set in the clusto db at
    initial instantiation time (when creating a brand new entity).

    >>> d.propA = 54
    >>> d.propA == 54
    True

    Several conventions are also exposed via the Driver interface.  
    
    """
    
    __metaclass__ = ClustoDriver

    _clustoType = "generic"
    _driverName = "entity"

    _properties = dict()


    @property
    def type(self):
        return self.entity.type

    @property
    def driver(self):
        return self.entity.driver

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
            return
        elif isinstance(nameDriverEntity, (str, unicode)):

            try:
                existing = clusto.getByName(nameDriverEntity)
            except LookupError, x:
                existing = None
            
            if existing:
                raise NameException("Driver with the name %s already exists."
                                    % (nameDriverEntity))


            self.entity = Entity(nameDriverEntity)
            self.entity.driver = self._driverName
            self.entity.type = self._clustoType

        else:
            raise TypeError("Could not create driver from given arguments.")

        for key, val in self._properties.iteritems():
            if key in kwargs:
                val = kwargs[key]
            if val is None:
                continue
            setattr(self, key, val)


    def __eq__(self, other):

        if isinstance(other, Entity):
            return self.entity.name == other.name
        elif isinstance(other, Driver):
            return self.entity.name == other.entity.name
        else:
            return False

    def __repr__(self):

        s = "%s(name=%s, type=%s, driver=%s)"

        return s % (self.__class__.__name__, self.entity.name, 
                    self.entity.type, self.entity.driver)

    def __cmp__(self, other):

        return cmp(self.name, other.name)

    def __hash__(self):
        return hash(self.entity.name)

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

        if not re.match('^[A-Za-z_]+[0-9A-Za-z_-]*$', key):

            raise NameException("Attribute name %s is invalid. "
                                "Attribute names may not contain periods or "
                                "comas." % key)
    

    def __getattr__(self, name):
        if name in self._properties:                
            if not self.hasAttr(name):
                return self._properties[name]
            attr = self.attrQuery(name, subkey='property', uniqattr=True)
            if not attr:
                return None
            else:
                return attr[0].value
        else:
            raise AttributeError("Attribute %s does not exist." % name)


    def __setattr__(self, name, value):

        if name in self._properties:
            a = self.attrQuery(name)
            if a:
                attr = a[0]             
                attr.value = value
            else:
                self.setAttr(name, value, subkey='property', uniqattr=True)
        else:
            object.__setattr__(self, name, value)
        
    @classmethod
    def ensureDriver(self, obj, msg=None):
        """Ensure that the given argument is a Driver.

        If the object is an Entity it will be turned into a Driver and then
        returned.  If it's a Driver it will be returned unaffected.  Otherwise
        a TypeError is raised with either a generic or given message.
        """
        
        if isinstance(obj, Entity):
            d = Driver(Entity)
        elif isinstance(obj, Driver):
            d = obj
        else:
            if not msg:
                msg = "Not a Driver."
            raise TypeError(msg)

        return d
        
    @classmethod
    def doAttrQuery(cls, key=(), value=(), number=(),
                    subkey=(), uniqattr=(), ignoreHidden=True, sortByKeys=True, 
                    glob=True, count=False, querybase=None, returnQuery=False,
                    entity=None):
        """Does queries against all Attributes using the DB."""

        clusto.flush()
        if querybase:
            query = querybase 
        else:
            query = SESSION.query(Attribute)

        ### This is bunk, gotta fix it
        if isinstance(cls, Driver):
            query = query.filter(and_(Attribute.entity_id==Entity.entity_id,
                                      Entity.driver == cls._driverName,
                                      Entity.type == cls._clustoType))

        if entity:
            query = query.filter_by(entity_id=entity.entity_id)

        if key is not ():
            if glob:
                query = query.filter(Attribute.key.like(key.replace('*', '%')))
            else:
                query = query.filter_by(key=key)

        if subkey is not ():
            if glob and subkey:
                query = query.filter(Attribute.subkey.like(subkey.replace('*', '%')))
            else:
                query = query.filter_by(subkey=subkey)

        if value is not ():
            typename = Attribute.getType(value)

            if typename == 'relation':
                if isinstance(value, Driver):
                    value = value.entity.entity_id
                query = query.filter_by(relation_id=value)

            else:
                query = query.filter_by(**{typename+'_value':value})

        if number is not ():
            if isinstance(number, bool):
                if number == True:
                    query = query.filter(Attribute.number != None)
                else:
                    query = query.filter(Attribute.number == None)
            elif isinstance(number, (int, long)):
                query = query.filter_by(number=number)
                
            else:
                raise TypeError("num must be either a boolean or an integer.")

        if uniqattr is not ():
            query = query.filter_by(uniqattr=uniqattr)

        if ignoreHidden:
            query.filter(not_(Attribute.key.like('_%')))

        if sortByKeys:
            query = query.order_by(Attribute.key)

        if count:
            return query.count()

        if returnQuery:
            return query

        return query.all()

    def attrQuery(self, *args, **kwargs):
        """Queries all attributes of *this* entity using the DB."""
        
        kwargs['entity'] = self.entity

        return self.doAttrQuery(*args, **kwargs)

    @classmethod
    def attrFilter(cls, attrlist, key=(), value=(), number=(), 
                   subkey=(), ignoreHidden=True, uniqattr=(),
                   sortByKeys=True, 
                   regex=False, 
                   clustoTypes=None,
                   clustoDrivers=None,
                   ):
        """Filter attribute lists. (Uses generator comprehension)

        Given a list of Attributes filter them based on exact matches of key,
        number, subkey, value, and/or uniqattr.

        There are some special cases:

        if number is True then the number variable must be non-null. if
        number is False then the number variable must be null.

        if ignoreHidden is True (the default) then filter out keys that begin
        with an underscore, if false don't filter out such keys.  If you
        specify a key that begins with an underscore as one of the arguments
        then ignoreHidden is assumed to be False.

        if sortByKeys is True then attributes are returned sorted by keys,
        otherwise their order is undefined.

        if regex is True then treat the key, subkey, and value query
        parameters as regular expressions.

        clustoTypes is a list of types that the entities referenced by
        relation attributes must match.

        clustoDrivers is a list of drivers that the entities referenced by
        relation attributes must match.
        """


        result = attrlist

        def subfilter(attrs, val, name):
            
            if regex:
                testregex = re.compile(val)
                result = (attr for attr in attrs 
                          if testregex.match(getattr(attr, name)))

            else:
                result = (attr for attr in attrs
                          if getattr(attr, name) == val)


            return result

        parts = ((key, 'key'), (subkey, 'subkey'), (value, 'value'))
        argattr = ((val,name) for val,name in parts if val is not ())

        for v, n in argattr:
            result = subfilter(result, v, n)


        if number is not ():
            if isinstance(number, bool):
                if number:
                    result = (attr for attr in result if attr.number is not None)
                else:
                    result = (attr for attr in result if attr.number is None)

            elif isinstance(number, (int, long)):
                result = (attr for attr in result if attr.number == number)
            
            else:
                raise TypeError("num must be either a boolean or an integer.")

                    
        if uniqattr is not ():
            result = (attr for attr in result if attr.uniqattr == uniqattr)

        if value:
            result = (attr for attr in result if attr.value == value)


        if key and key.startswith('_'):
            ignoreHidden = False

        if ignoreHidden:
            result = (attr for attr in result if not attr.key.startswith('_'))

        if clustoDrivers:
            cdl = [clusto.getDriverName(n) for n in clustoDrivers]
            result = (attr for attr in result if attr.isRelation and attr.value.entity.driver in cdl)

        if clustoTypes:
            ctl = [clusto.getTypeName(n) for n in clustoTypes]
            result = (attr for attr in result if attr.isRelation and attr.value.entity.type in ctl)
            
        if sortByKeys:
            result = sorted(result)

        
        return list(result)

    def _itemizeAttrs(self, attrlist):
        return [(x.keytuple, x.value) for x in attrlist]
        
    def attrs(self, *args, **kwargs):
        """Return attributes for this entity.

        (filters whole attribute list as opposed to querying the db directly)
        """

        if 'mergeContainerAttrs' in kwargs:
            mergeContainerAttrs = kwargs.pop('mergeContainerAttrs')
        else:
            mergeContainerAttrs = False

        attrs = self.attrFilter(self.entity._attrs, *args, **kwargs) 

        if mergeContainerAttrs:
            kwargs['mergeContainerAttrs'] = mergeContainerAttrs
            for parent in self.parents():
                attrs.extend(parent.attrs(*args,  **kwargs))

        return attrs

    def attrValues(self, *args, **kwargs):
        """Return the values of the attributes that match the given arguments"""

        return [k.value for k in self.attrs(*args, **kwargs)]

    def references(self, *args, **kwargs):
        """Return the references to this Thing. The references are attributes. 

        Accepts the same arguments as attrs().

        The semantics of clustoTypes and clustoDrivers changes to match the
        clustoType or clustoDriver of the Entity that owns the attribute as
        opposed to the Entity the attribute refers to.
        """

        
        clustoDrivers = kwargs.pop('clustoDrivers', None)
            
        clustoTypes = kwargs.pop('clustoTypes', None)
        
        result = self.attrFilter(self.entity._references, *args, **kwargs)

        if clustoDrivers:
            cdl = [clusto.getDriverName(n) for n in clustoDrivers]
            result = (attr for attr in result if attr.entity.driver in cdl)

        if clustoTypes:
            ctl = [clusto.getTypeName(n) for n in clustoTypes]
            result = (attr for attr in result if attr.entity.type in ctl)


        return list(result)

    def referencers(self, *args, **kwargs):
        """Return the Things that reference _this_ Thing.
        
        Accepts the same arguments as references() but adds an instanceOf filter
        argument.
        """
        
        refs = [Driver(a.entity) for a in sorted(self.references(*args, **kwargs),
                                                 lambda x,y: cmp(x.attr_id,
                                                                 y.attr_id))]

        return refs

                   
    def attrKeys(self, *args, **kwargs):

        return [x.key for x in self.attrs(*args, **kwargs)]

    def attrKeyTuples(self, *args, **kwargs):

        return [x.keytuple for x in self.attrs(*args, **kwargs)]

    def attrItems(self, *args, **kwargs):
        return self._itemizeAttrs(self.attrs(*args, **kwargs))

    def addAttr(self, key, value=(), number=(), subkey=(), uniqattr=False):
        """add a key/value to the list of attributes

        if number is True, create an attribute with the next available
        otherwise number just gets passed to the Attribute constructor so it
        can be an integer or an sqlalchemy expression
        
        An optional subkey can also be specified. Subkeys don't affect
        numbering by default.
        """

        if isinstance(key, Attribute):
            self.entity._attrs.append(key)
            return key
        
        self._checkAttrName(key)
        if subkey:
            self._checkAttrName(subkey)

        if isinstance(value, Driver):
            value = value.entity

        if number is ():
            number = None
        if subkey is ():
            subkey = None


        attr = Attribute(key, value, subkey=subkey, number=number, uniqattr=uniqattr)
        self.entity._attrs.append(attr)

        return attr

    def delAttrs(self, *args, **kwargs):
        "delete attribute with the given key and value optionally value also"

        clusto.flush()
        for i in self.attrQuery(*args, **kwargs):
            self.entity._attrs.remove(i)
            i.delete()
        clusto.flush()


    def setAttr(self, key, value, number=(), subkey=(), uniqattr=()):
        """replaces all attributes with the given key"""
        self._checkAttrName(key)
        self.delAttrs(key=key, number=number, subkey=subkey, uniqattr=uniqattr)
        
        return self.addAttr(key, value, number=number, subkey=subkey, uniqattr=uniqattr)
        

    
    def hasAttr(self, *args, **kwargs):
        """return True if this list has an attribute with the given key"""

        for i in self.attrQuery(*args, **kwargs):
            return True

        return False
    
    def insert(self, thing):
        """Insert the given Enity or Driver into this Entity.  Such that:

        >>> A.insert(B)
        >>> (B in A) 
        True


        """
        
        d = self.ensureDriver(thing, 
                              "Can only insert an Entity or a Driver. "
                              "Tried to insert %s." % str(type(thing)))


        parent = thing.parents()

        if parent:
            raise TypeError("%s is already in %s and cannot be inserted into %s."
                            % (d.name, parent[0].entity.name, self.name))

        self.addAttr("_contains", d, number=True)
        
    def remove(self, thing):
        """Remove the given Entity or Driver from this Entity. Such that:
        
        >>> A.insert(B)
        >>> B in A
        True
        >>> A.remove(B)
        >>> B in A
        False

        """
        if isinstance(thing, Entity):
            d = Driver(Entity)
        elif isinstance(thing, Driver):
            d = thing
        else:
            raise TypeError("Can only remove an Entity or a Driver. "
                            "Tried to remove %s." % str(type(thing)))


        self.delAttrs("_contains", d, ignoreHidden=False)

    def contentAttrs(self, *args, **kwargs):
        """Return the attributes referring to this Thing's contents

        """

        attrs = self.attrs("_contains", *args, **kwargs) 

        return attrs

    def contents(self, *args, **kwargs):
        """Return the contents of this Entity.  Such that:

        >>> A.insert(B)
        >>> A.insert(C)
        >>> A.contents()
        [B, C]
        
        """
        
        return [attr.value for attr in self.contentAttrs(*args, **kwargs)]

    def parents(self, **kwargs):        
        """Return a list of Things that contain _this_ Thing. """

        parents = self.referencers('_contains', **kwargs)

        return parents
                       
    @classmethod
    def getByAttr(cls, *args, **kwargs):
        """Get list of Drivers that have by attributes search """
        
        attrlist = cls.doAttrQuery(*args, **kwargs)

        objs = [Driver(x.entity) for x in attrlist]

        return objs
            

    
    @property
    def name(self):
        return self.entity.name
