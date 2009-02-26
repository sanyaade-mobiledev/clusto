
import re
import itertools

import clusto
from clusto.schema import *
from clusto.exceptions import *

from clustodriver import *


class Driver(object):
    """Base Driver."""
    
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
    def doAttrQuery(cls, key=(), value=(), numbered=(),
                    subkey=(), uniqattr=(), ignoreHidden=True, sortByKeys=True, 
                    glob=True, count=False, querybase=None, returnQuery=False,
                    entity=None):
        """Does queries against all Attributes."""

        clusto.flush()
        if querybase:
            query = querybase 
        else:
            query = SESSION.query(Attribute)

        if issubclass(cls, Driver):         
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

        if numbered is not ():
            if isinstance(numbered, bool):
                if numbered == True:
                    query = query.filter(Attribute.number != None)
                else:
                    query = query.filter(Attribute.number == None)
            elif isinstance(numbered, (int, long)):
                query = query.filter_by(number=numbered)
                
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
        
        kwargs['entity'] = self.entity

        return self.doAttrQuery(*args, **kwargs)

    def _attrFilter(self, attrlist, key=(), value=(), numbered=(), 
                    subkey=(), ignoreHidden=True, uniqattr=(),
                    sortByKeys=True, 
                    regex=False, 
                    clustoTypes=None,
                    clustoDrivers=None,
                    ):
        "Filter various kinds of attribute lists."


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


        if numbered is not ():
            if isinstance(numbered, bool):
                if numbered:
                    result = (attr for attr in result if attr.number is not None)
                else:
                    result = (attr for attr in result if attr.number is None)

            elif isinstance(numbered, (int, long)):
                result = (attr for attr in result if attr.number == numbered)
            
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
            result = (attr for attr in result if attr.entity.driver in cdl)

        if clustoTypes:
            ctl = [clusto.getTypeName(n) for n in clustoTypes]
            result = (attr for attr in result if attr.entity.type in ctl)
            
        if sortByKeys:
            result = sorted(result)

        
        return list(result)

    def _itemizeAttrs(self, attrlist):
        return [(x.keytuple, x.value) for x in attrlist]
        
    def attrs(self, *args, **kwargs):
        """Return attributes for this entity. """

        if 'mergeContainerAttrs' in kwargs:
            mergeContainerAttrs = kwargs.pop('mergeContainerAttrs')
        else:
            mergeContainerAttrs = False

        attrs = self._attrFilter(self.entity._attrs, *args, **kwargs) 

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

        Accepts the same arguments as attrs() except for meregeContainerAttrs.
        Also adds clustotype and clustodriver filter parameters.
        """


        attrs = self._attrFilter(self.entity._references, *args, **kwargs)

        return list(attrs)

    def referencers(self, *args, **kwargs):
        """Return the Things that reference _this_ Thing.
        
        Accepts the same arguments as references() but adds an instanceOf filter
        argument.
        """
        
        refs = [Driver(a.entity) for a in sorted(self.references(*args, **kwargs),
                                                 lambda x,y: cmp(x.attr_id,
                                                                 y.attr_id))]

        return refs

        


#       if clustotype or clustodriver:
#           query = query.filter(Entity.entity_id == Attribute.entity_id)
#           if clustodriver:
#               query = query.filter(Entity.driver == clustodriver)
#           if clustotype:
#               query = query.filter(Entity.typ == clustotype)
 
#         attrs = self._attrQuery(query, *args, **kwargs)

#        return attrs
                   
    def attrKeys(self, *args, **kwargs):

        return [x.key for x in self.attrs(*args, **kwargs)]

    def attrKeyTuples(self, *args, **kwargs):

        return [x.keytuple for x in self.attrs(*args, **kwargs)]

    def attrItems(self, *args, **kwargs):
        return self._itemizeAttrs(self.attrs(*args, **kwargs))

    def addAttr(self, key, value, numbered=(), subkey=(), uniqattr=False):
        """add a key/value to the list of attributes

        if numbered is True, create an attribute with the next available
        otherwise numbered just gets passed to the Attribute constructor so it
        can be an integer or an sqlalchemy expression
        
        An optional subkey can also be specified. Subkeys don't affect
        numbering by default.
        """

        self._checkAttrName(key)
        if subkey:
            self._checkAttrName(subkey)

        if isinstance(value, Driver):
            value = value.entity

        if numbered is ():
            numbered = None
        if subkey is ():
            subkey = None

        if isinstance(numbered, bool) and numbered == True:
            numbered = select([func.count('*')], and_(ATTR_TABLE.c.key==key,
                                                      ATTR_TABLE.c.number!=None)).as_scalar() 


        attr = Attribute(key, value, subkey=subkey, number=numbered, uniqattr=uniqattr)
        self.entity._attrs.append(attr)

        return attr

    def delAttrs(self, *args, **kwargs):
        "delete attribute with the given key and value optionally value also"

        clusto.flush()
        for i in self.attrQuery(*args, **kwargs):
            self.entity._attrs.remove(i)
            i.delete()
        clusto.flush()


    def setAttr(self, key, value, numbered=(), subkey=(), uniqattr=()):
        """replaces all attributes with the given key"""
        self._checkAttrName(key)
        self.delAttrs(key=key, numbered=numbered, subkey=subkey, uniqattr=uniqattr)
        
        return self.addAttr(key, value, numbered=numbered, subkey=subkey, uniqattr=uniqattr)
        

    
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

        self.addAttr("_contains", d, numbered=True)
        
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
