"""
Clusto schema

"""

#from sqlalchemy import DynamicMetaData, create_session, select, and_, relation
#from sqlalchemy import Table, Column, ForeignKey, String, Integer
from sqlalchemy import *

from sqlalchemy.ext.sessioncontext import SessionContext
from sqlalchemy.ext.assignmapper import assign_mapper

from clusto.sqlalchemyhelpers import ClustoMapperExtension

import sys
# session context


METADATA = DynamicMetaData()


CTX = SessionContext(create_session)

THING_TABLE = Table('things', METADATA,
                    Column('name', String(128), primary_key=True),
                    #Column('thingtype', String(128)),
                    mysql_engine='InnoDB'
                    )

ATTR_TABLE = Table('thing_attrs', METADATA,
                   Column('attr_id', Integer, primary_key=True),
                   Column('thing_name', String(128),
                          ForeignKey('things.name', ondelete="CASCADE",
                                     onupdate="CASCADE")),
                   Column('key', String(1024)),
                   Column('value', String),
                   mysql_engine='InnoDB'
                   )

THINGTHING_TABLE = Table('thing_thing', METADATA,
                         Column('thing_name1', String(128),
                                ForeignKey('things.name', ondelete="CASCADE",
                                           onupdate="CASCADE"),
                                primary_key=True),
                         Column('thing_name2', String(128),
                                ForeignKey('things.name', ondelete="CASCADE",
                                           onupdate="CASCADE"),
                                primary_key=True),
                         mysql_engine='InnoDB'
                         )


class Attribute(object):
    """
    Attribute class holds key/value pair backed by DB
    """
    def __init__(self, key, value, thing_name=None):
        self.key = key
        self.value = value

        if thing_name:
            self.thing_name = thing_name

    def __repr__(self):
        return "thingname: %s, keyname: %s, value: %s" % (self.thing_name,
                                                          self.key,
                                                          self.value)

assign_mapper(CTX, Attribute, ATTR_TABLE)


class AttributeDict(dict):
    """
    This is a Multi-valued Attribute Dict

    This behaves much like a normal dict except that all values are lists.

    When setting values the following rules apply:
        if the key does not exist and the value is a scalar then the value is
        put into a new list pointed to by the key.

        if the key does exist and the value is a scalar then the value is
        appended to the list of values pointed to by that key.

        if the value is a list then the value gets set to the given list and
        any old values for that key are discarded.
    """

    def __init__(self, somedict=None):

        if somedict:

            if isinstance(somedict, dict):
                for i in somedict:
                    self[i] = somedict[i]
            elif isinstance(somedict, list):
                for i in somedict:
                    self[i[0]] = i[1]
        else:
            super(dict, self).__init__()
        
        
        
    def append(self, item):
        """Add an item to the dictionary"""
        self[item.key] = item 
    def __iter__(self): 
        return self.itervalues()  
    def __setitem__(self, key, value):
        if isinstance(value, list):
            dict.__setitem__(self, key, value)
        else:
            self.setdefault(key, []).append(value)

    def items(self):
        items = []

        for key in self.keys():
            for value in self[key]:
                items.append((key, value))

        return items
            
    def update(self, somedict, replace=False):

        for key in somedict:
            self[key] = somedict[key]
        

DRIVERLIST = set()

class ClustoThing(type):
    """
    Metaclass for all clusto stored objects
    """
    def __init__(cls, name, bases, dct):

        if not cls.meta_attrs.has_key('clustotype'):
            ## I should do something clever if it's missing
            raise DriverException("Driver %s missing clustotype meta_attrs"
                                  % cls.__name__)
        
        tempattrs = AttributeDict()

        for klass in bases:
            if hasattr(klass, 'meta_attrs'):
                tempattrs.update(klass.meta_attrs)

        tempattrs.update(cls.meta_attrs)

        cls._all_meta_attrs = tempattrs
        DRIVERLIST.add(cls)

        if cls.meta_attrs['clustotype'] != 'thing':
            selection = select([THING_TABLE],
                               and_(ATTR_TABLE.c.key=='clustotype',
                                    ATTR_TABLE.c.value==cls.meta_attrs['clustotype'],
                                    ATTR_TABLE.c.thing_name==THING_TABLE.c.name)
                               ).alias(cls.meta_attrs['clustotype']+'alias')

        else:
            selection = THING_TABLE
            
        
        assign_mapper(CTX, cls, selection, properties={
            '_attrs' : relation(Attribute, lazy=False,
                                cascade='all, delete-orphan',)
                },
                      extension=ClustoMapperExtension())

        super(ClustoThing, cls).__init__(name, bases, dct)



    
class ThingAssociation(object):
    """
    Relationship between two Things
    """
    def __init__(self, thing1, thing2):
        self.thing_name1 = thing1.name
        self.thing_name2 = thing2.name

assign_mapper(CTX, ThingAssociation, THINGTHING_TABLE)

class DriverException(Exception):
    """exception for driver errors"""
    pass
