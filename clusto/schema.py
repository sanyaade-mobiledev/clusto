"""
Clusto schema

"""
VERSION = 0.1
from sqlalchemy import *

import sqlalchemy.exceptions

from sqlalchemy.ext.sessioncontext import SessionContext
from sqlalchemy.ext.assignmapper import assign_mapper

from sqlalchemy.orm import * #Mapper, MapperExtension
from sqlalchemy.orm.mapper import Mapper

from sqlalchemy.orm import mapperlib


import sys
import datetime


METADATA = MetaData()


SESSION = scoped_session(sessionmaker(autoflush=True, transactional=True)) 

ENTITY_TABLE = Table('entities', METADATA,
                    Column('entity_id', Integer, primary_key=True),
                    Column('name', Unicode(1024), unique=True, nullable=False),
                    Column('type', Unicode(64), nullable=False),
                    Column('driver', Unicode(64), nullable=False),
                    mysql_engine='InnoDB'
                    )

ATTR_TABLE = Table('entity_attrs', METADATA,
                   Column('attr_id', Integer, primary_key=True),
                   Column('entity_id', Integer,
                          ForeignKey('entities.entity_id'), nullable=False),
                   Column('key', Unicode(1024)),
                   Column('datatype', Unicode(32)),

                   Column('int_value', Integer, default=None),
                   Column('string_value', Unicode, default=None),
                   Column('datetime_value', DateTime, default=None),
                   Column('relation_id', Integer,
                          ForeignKey('entities.entity_id'), default=None),
                   )


TRANSACTION_TABLE = Table('transactions', METADATA,
                          Column('txn_id', Integer, primary_key=True),
                          Column('entity_name', Unicode(1024),
                                 nullable=False),
                          Column('function', Unicode),
                          Column('args', Unicode),
                          Column('timestamp', DateTime),
                          )
                          

class Attribute(object):
    """
    Attribute class holds key/value pair backed by DB
    """
    def __init__(self, key, value):

        sess = create_session()

        self.key = key
        
        self.value = value

    def __cmp__(self, other):
        return cmp(self.key, other.key)
    
    def __eq__(self, other):

        return ((self.key == other.key) and (self.value == other.value))
    
    def __str__(self):

        if self.datatype == 'relation':
            value = self.relation_value.name
        else:
            value = self.value
        
        return "%s.%s.%s %s" % (self.entity.name, self.key,
                                self.datatype, value)
        
    def _get_value(self):
        return getattr(self, self.datatype + "_value")

    def _set_value(self, value):
        if isinstance(value, int):
            self.datatype = 'int'
        elif isinstance(value, datetime.datetime):
            self.datatype = 'datetime'
        elif isinstance(value, Entity):
            self.datatype = 'relation'
        elif hasattr(value, 'entity') and isinstance(value.entity, Entity):
            self.datatype = 'relation'
            value = value.entity
        else:
            self.datatype = 'str'
            value = str(value)

        setattr(self, self.datatype + "_value", value)

    value = property(_get_value, _set_value)

    def delete(self):

        try:
            SESSION.delete(self)
        except sqlalchemy.exceptions.InvalidRequestError:
            SESSION.expunge(self)



class Entity(object):
    """
    The base object that can be stored and managed in clusto.

    An entity can have a name, type, and attributes.

    An Entity's functionality is augmented by drivers which get included
    as mixins.  
    """
    meta_attrs = {}

    required_attrs = ()
    
    def __init__(self, name, driver='entity', clustotype='entity'):
        """
        Initialize an Entity.

        @param name: the name of the new Entity
        @type name: C{str}
        @param attrslist: the list of key/value pairs to be set as attributes
        @type attrslist: C{list} of C{tuple}s of length 2
        """
        
        self.name = unicode(name)

        self.driver = driver
        self.type = clustotype


        
    def __eq__(self, otherentity):
        """
        Am I the same as the Other Entity.

        @param otherentity: the entity you're comparing with
        @type otherentity: L{Entity}
        """

        ## each Thing must have a unique name so I'll just compare those

        return self.name == otherentity.name

    def __cmp__(self, other):

        return cmp(self.name, other.name)


    def __str__(self):
        """
        Output this entity in configrc format
        """
        out = []
        for attr in self._attrs:
            out.append(str(attr))

        out.append("%s.clustodriver.string %s" % (self.name, self.driver))
            
        return '\n'.join(out)


    def delete(self):
        """
        Delete self and all references to self.
        """

        try:
            SESSION.delete(self)
        except sqlalchemy.exceptions.InvalidRequestError:
            SESSION.expunge(self)
        #SESSION.delete(self)

        q = SESSION.query(Attribute).filter_by(relation_id=self.entity_id)

        for i in q:
            i.delete()
    


SESSION.mapper(Attribute, ATTR_TABLE,
               properties = {'relation_value': relation(Entity, lazy=True, 
                                                        primaryjoin=ATTR_TABLE.c.relation_id==ENTITY_TABLE.c.entity_id,
                                                        uselist=False)})


## might be better to make the relationships here dynamic_loaders in the long
## term.
SESSION.mapper(Entity, ENTITY_TABLE,
               properties={'_attrs' : relation(Attribute, lazy=True,
                                               cascade="all, delete, delete-orphan",
                                               primaryjoin=ENTITY_TABLE.c.entity_id==ATTR_TABLE.c.entity_id,
                                               backref='entity'),
                           '_references' : relation(Attribute, lazy=True,
                                                    cascade="all, delete, delete-orphan",
                                                    primaryjoin=ENTITY_TABLE.c.entity_id==ATTR_TABLE.c.relation_id)
                           }
               )
        

