
from sqlalchemy.orm import Mapper, MapperExtension
from sqlalchemy.ext.associationproxy import _AssociationDict

_NotProvided = object()

class _AssociationMultiDict(_AssociationDict):
    """Generic proxying list which proxies dict operations to a another dict,
    converting association objects to and from a simplified value.
    """

    def __init__(self, collection, creator, attr):
        """
        collection
          A list-based collection of entities (usually an object attribute
          managed by a SQLAlchemy relation())
          
        creator
          A function that creates new target entities.  Given two parameters:
          key and value.  The assertion is assumed:
            obj = creator(somekey, somevalue)
            assert getter(somekey) == somevalue

        getter
          A function.  Given an associated object and a key, return the 'value'.

        setter
          A function.  Given an associated object, a key and a value, store
          that value on the object.
        """

        self.value_attr = attr
        self.col = collection
        self.creator = creator
        #self.getter = lambda o: self._doGet(o)
        #self.setter = lambda o, k, v: self._doSet(o, v)
        self.getter = lambda o: getattr(o, attr)
        self.setter = lambda o, k, v: setattr(o, attr, v)

    def _doGet(self, obj):

        if isinstance(obj, list):
            retval = []
            for i in obj:
                retval.append(getattr(i, self.value_attr))
        else:        
            retval = getattr(obj, self.value_attr)

        return retval

    def _doSet(self, obj, value):

        if isinstance(value, list):
            setattr(obj, self.value_attr, value)
            return
        
        if hasattr(obj, self.value_attr):
            self._doGet(obj).append(value)
        else:
            setattr(obj, self.value_attr, value)


    def _create(self, key, value):
        return self.creator(key, value)

    def _get(self, object):
        retval = []
        if isinstance(object, list):
            for i in object:
                retval.append(self.getter(i))
        else:
            retval = [self.getter(object)]

        return retval

    def _set(self, object, key, value):
        return self.setter(object, key, value)

    def __len__(self):
        return len(self.col)

    def __nonzero__(self):
        if self.col:
            return True
        else:
            return False

    def __getitem__(self, key):
        
        return self._get(self.col[key])
    
    def __setitem__(self, key, value):
        if key in self.col:
            if isinstance(value, list):
                for item in self.col[key]:
                    del(item)

                self.pop(key)
                
                
                for val in value:
                    self.col[key] = self._create(key,val)
            else:
                self.col[key] = self._create(key,value)

        else:
            self.col[key] = self._create(key, value)

    def __delitem__(self, key):
        for item in self.col[key]:
            del(item)
        self.pop(key)
        #del self.col[key]

    def __iter__(self):
        return iter(self.col)

    def clear(self):
        self.col.clear()


    def __repr__(self):
        return repr(dict(self.items()))

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def setdefault(self, key, default=None):
        if key not in self.col:
            self.col[key] = self._create(key, default)
            return default
        else:
            return self[key]

    def keys(self):
        return self.col.keys()
    def iterkeys(self):
        return self.col.iterkeys()

    def values(self):
        return [ self._get(member) for member in self.col.values() ]
    def itervalues(self):
        for key in self.col:
            yield self._get(self.col[key])
        raise StopIteration

    def items(self):
        return [(k, self._get(self.col[k])) for k in self.keys()]
    def iteritems(self):
        for key in self.col:
            yield (key, self._get(self.col[key]))
        raise StopIteration

    def pop(self, key, default=_NotProvided):
        if default is _NotProvided:
            member = self.col.pop(key)
        else:
            member = self.col.pop(key, default)
        return self._get(member)

    def popitem(self):
        item = self.col.popitem()
        return (item[0], self._get(item[1]))
    
    def update(self, *a, **kw):
        if len(a) > 1:
            raise TypeError('update expected at most 1 arguments, got %i' %
                            len(a))
        elif len(a) == 1:
            seq_or_map = a[0]
            for item in seq_or_map:
                if isinstance(item, tuple):
                    self[item[0]] = item[1]
                else:
                    self[item] = seq_or_map[item]

        for key, value in kw:
            self[key] = value

    def copy(self):
        return dict(self.items())





class ClustoMapperExtension(MapperExtension):

    def populate_instance(self, mapper, selectcontext, row, instance, identitykey, isnew):
        """called right before the mapper, after creating an instance from a row, passes the row
        to its MapperProperty objects which are responsible for populating the object's attributes.
        If this method returns EXT_PASS, it is assumed that the mapper should do the appending, else
        if this method returns any other value or None, it is assumed that the append was handled by this method.

        Essentially, this method is used to have a different mapper populate the object:

            def populate_instance(self, mapper, selectcontext, instance, row, identitykey, isnew):
                othermapper.populate_instance(selectcontext, instance, row, identitykey, isnew, frommapper=mapper)
                return True
        """

        Mapper.populate_instance(mapper, selectcontext, instance, row, identitykey, isnew)
        instance._setProperClass()
        return True
