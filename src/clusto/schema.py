"""
Clusto schema

"""
VERSION = 0.1
from sqlalchemy import *

from sqlalchemy.exceptions import InvalidRequestError

#from sqlalchemy.ext.sessioncontext import SessionContext
#from sqlalchemy.ext.assignmapper import assign_mapper

from sqlalchemy.orm import * #Mapper, MapperExtension
from sqlalchemy.orm.mapper import Mapper

from sqlalchemy.orm import mapperlib
import sqlalchemy.sql

import re
import sys
import datetime
import clusto

__all__ = ['ATTR_TABLE', 'Attribute', 'and_', 'ENTITY_TABLE', 'Entity', 'func',
	   'METADATA', 'not_', 'or_', 'SESSION', 'select', 'VERSION', ]

METADATA = MetaData()


SESSION = scoped_session(sessionmaker())#autoflush=True, autocommit=True)) 

ENTITY_TABLE = Table('entities', METADATA,
                    Column('entity_id', Integer, primary_key=True),
                    Column('name', String(1024, convert_unicode=True,
                           assert_unicode=None), unique=True,
                           nullable=False, ),
                    Column('type', String(64), nullable=False),
                    Column('driver', String(64), nullable=False),
                    mysql_engine='InnoDB'
                    )

ATTR_TABLE = Table('entity_attrs', METADATA,
                   Column('attr_id', Integer, primary_key=True),
                   Column('entity_id', Integer,
                          ForeignKey('entities.entity_id'), nullable=False),
                   Column('key', String(1024, convert_unicode=True,
                           assert_unicode=None),),
                   Column('subkey', String(1024, convert_unicode=True,
                           assert_unicode=None), nullable=True,
                          default=None, ),
                   Column('number', Integer, nullable=True, default=None),
                   Column('uniqattr', Boolean, nullable=True, default=None),
                   Column('datatype', String(32), default='string', nullable=False),

                   Column('int_value', Integer, default=None),
                   Column('string_value', Text(convert_unicode=True,
                           assert_unicode=None), default=None,),
                   Column('datetime_value', DateTime, default=None),
                   Column('relation_id', Integer,
                          ForeignKey('entities.entity_id'), default=None),

                   )
Index('key_num_subkey_idx', 
      ATTR_TABLE.c.entity_id, ATTR_TABLE.c.key, 
      ATTR_TABLE.c.number, ATTR_TABLE.c.subkey, ATTR_TABLE.c.uniqattr,
      unique=True)

class Attribute(object):
    "Attribute class holds key/value pair backed by DB"

    def __init__(self, key, value, subkey=None, number=None, uniqattr=False):

        self.key = key
        
        self.value = value

	self.subkey = subkey

	self.number = number

	if not uniqattr:
	    self.uniqattr = None
	else:
	    self.uniqattr = True
	
    def __cmp__(self, other):

	if not isinstance(other, Attribute):
	    raise TypeError("Can only compare equality with an Attribute. "
			    "Got a %s instead." % (type(other).__name__))

        return cmp(self.key, other.key)
    
    def __eq__(self, other):

	if not isinstance(other, Attribute):
	    return False

        return ((self.key == other.key) and (self.value == other.value))

    def __repr__(self):
	
	s = "%s(key=%s, value=%s, subkey=%s, number=%s)"

	return s % (self.__class__.__name__, 
		    self.key, self.value, self.subkey, self.number)

    def __str__(self):

        if self.datatype == 'relation':
            value = self.relation_value.name
        else:
            value = self.value

        entityname = (self.entity and self.entity.name) or None
        return "%s|%s|%s %s" % (entityname, self.fullkey,
                                self.datatype, value)

    def getValueType(self, value=None):
        if value == None:
            if self.datatype == None:
                valtype = "string"
            else:
                valtype = self.datatype
        else:
            valtype = self.getType(value)
        
        return valtype + "_value"

    @property
    def keytuple(self):
	return (self.key, self.number, self.subkey)

    @classmethod
    def getType(self, value):

        if isinstance(value, int):
            datatype = 'int'
        elif isinstance(value, datetime.datetime):
            datatype = 'datetime'
        elif isinstance(value, Entity):
            datatype = 'relation'
        elif hasattr(value, 'entity') and isinstance(value.entity, Entity):
            datatype = 'relation'
        else:
            datatype = 'string'

        return datatype
        
        
    def _get_value(self):

	if self.getValueType() == 'relation_value':
	    return clusto.drivers.base.Driver(getattr(self, self.getValueType()))
	else:
	    return getattr(self, self.getValueType())

    def _set_value(self, value):
	
	if not isinstance(value, sqlalchemy.sql.ColumnElement):
	    self.datatype = self.getType(value)

        setattr(self, self.getValueType(value), value)



    value = property(_get_value, _set_value)

    def delete(self):
        ### TODO this seems like a hack
        
        try:
            SESSION.delete(self)
        except InvalidRequestError:
            pass #SESSION.expunge(self)



class Entity(object):
    """
    The base object that can be stored and managed in clusto.

    An entity can have a name, type, and attributes.

    An Entity's functionality is augmented by drivers which get included
    as mixins.  
    """
    
    def __init__(self, name, driver='entity', clustotype='entity'):
        """Initialize an Entity.

        @param name: the name of the new Entity
        @type name: C{str}
        @param attrslist: the list of key/value pairs to be set as attributes
        @type attrslist: C{list} of C{tuple}s of length 2
        """

        self.name = name

        self.driver = driver
        self.type = clustotype


        
    def __eq__(self, otherentity):
        """Am I the same as the Other Entity.

        @param otherentity: the entity you're comparing with
        @type otherentity: L{Entity}
        """

        ## each Thing must have a unique name so I'll just compare those
        if not isinstance(otherentity, Entity):
            retval = False
        else:
            retval = self.name == otherentity.name
        
        return retval

    def __cmp__(self, other):

        if not hasattr(otherentity, 'name'):
	    raise TypeError("Can only compare equality with an Entity-like "
			    "object.  Got a %s instead." 
			    % (type(other).__name__))

        return cmp(self.name, other.name)


    def __repr__(self):
	s = "%s(name=%s, driver=%s, clustotype=%s)"

	return s % (self.__class__.__name__, 
		    self.name, self.driver, self.type)

    def __str__(self):
        "Return string representing this entity"
            
        return "%s.clustodriver.string %s" % (self.name, self.driver)
            

    def delete(self):
        "Delete self and all references to self."

        try:
            SESSION.delete(self)
        except InvalidRequestError:
            SESSION.expunge(self)
        #SESSION.delete(self)

        q = SESSION.query(Attribute).filter_by(relation_id=self.entity_id)

        for i in q:
            i.delete()
    


SESSION.mapper(Attribute, ATTR_TABLE,
               properties = {'relation_value': relation(Entity, lazy=True, 
                                                        primaryjoin=ATTR_TABLE.c.relation_id==ENTITY_TABLE.c.entity_id,
                                                        uselist=False,
                                                        passive_updates=False)})


## might be better to make the relationships here dynamic_loaders in the long
## term.
SESSION.mapper(Entity, ENTITY_TABLE,
               properties={'_attrs' : relation(Attribute, lazy='dynamic',
                                               cascade="all, delete, delete-orphan",
                                               primaryjoin=ENTITY_TABLE.c.entity_id==ATTR_TABLE.c.entity_id,
                                               backref='entity',
                                               passive_updates=False,
                                               uselist=True),
                           '_references' : relation(Attribute, lazy='dynamic',
                                                    cascade="all, delete, delete-orphan",
                                                    primaryjoin=ENTITY_TABLE.c.entity_id==ATTR_TABLE.c.relation_id,
                                                    passive_updates=False,
                                                    uselist=True)
                           }
               )
        

