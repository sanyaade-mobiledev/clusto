"""
Clusto schema

"""
VERSION = 3
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
           'METADATA', 'not_', 'or_', 'SESSION', 'select', 'VERSION',
           'latest_version', 'CLUSTO_VERSIONING']


METADATA = MetaData()


CLUSTO_VERSIONING = Table('clustoversioning', METADATA,
                          Column('version', Integer, primary_key=True),
                          Column('timestamp', TIMESTAMP, default=func.current_timestamp()),
                          )


class ClustoSession(sqlalchemy.orm.interfaces.SessionExtension):

    def before_commit(self, session):
        session.execute(CLUSTO_VERSIONING.insert().values())
        return EXT_CONTINUE
        

SESSION = scoped_session(sessionmaker(autoflush=True, autocommit=True,
                                      extension=ClustoSession()))


def latest_version():
    return select([func.max(CLUSTO_VERSIONING.c.version)])



ENTITY_TABLE = Table('entities', METADATA,
                     Column('entity_id', Integer, primary_key=True),
                     Column('name', String(128, convert_unicode=True,
                                           assert_unicode=None), unique=True,
                            nullable=False, ),
                     Column('type', String(32), nullable=False),
                     Column('driver', String(32), nullable=False),
                     Column('version', Integer, nullable=False),
                     Column('deleted_at_version', Integer, default=None),
                     
                     mysql_engine='InnoDB'
                     )

ATTR_TABLE = Table('entity_attrs', METADATA,
                   Column('attr_id', Integer, primary_key=True),
                   Column('entity_id', Integer,
                          ForeignKey('entities.entity_id'), nullable=False),
                   Column('key', String(256, convert_unicode=True,
                           assert_unicode=None),),
                   Column('subkey', String(256, convert_unicode=True,
                           assert_unicode=None), nullable=True,
                          default=None, ),
                   Column('number', Integer, nullable=True, default=None),
                   Column('datatype', String(32), default='string', nullable=False),

                   Column('int_value', Integer, default=None),
                   Column('string_value', Text(convert_unicode=True,
                           assert_unicode=None), default=None,),
                   Column('datetime_value', DateTime, default=None),
                   Column('relation_id', Integer,
                          ForeignKey('entities.entity_id'), default=None),

                   Column('version', Integer, nullable=False),
                   Column('deleted_at_version', Integer, default=None),
                   mysql_engine='InnoDB'

                   )

class ClustoVersioning(object):
    pass

class Attribute(object):
    """Attribute class holds key/value pair

    An Attribute is a DB backed object that holds a key, number, subkey,
    and a value.

    Each Attribute is associated with an Entity.

    There can be multiple attributes with the same key, number, subkey, and/or
    value.  

    Optionally you can explicitely set int_value, string_value,
    datetime_value, relation_id, and datatype.  These settings would override
    the values set by passing in 'value'.
    """

    def __init__(self, entity, key, value=None,
                 subkey=None, number=None,
                 int_value=None, string_value=None,
                 datetime_value=None, relation_id=None, datatype=None):

        self.entity = entity
        self.key = key
        
        self.value = value

        self.subkey = subkey

        if isinstance(number, bool) and number == True:
            self.number = select([func.coalesce(select([func.max(ATTR_TABLE.c.number)+1], 
                                                       and_(ATTR_TABLE.c.key==key,
                                                            ATTR_TABLE.c.number!=None,
                                                            )).as_scalar(), 0)])

        else:
            self.number = number

        if int_value is not None: self.int_value = int_value
        if string_value is not None: self.string_value = sting_value
        if datetime_value is not None: self.datetime_value = datetime_value
        if relation_id is not None: self.relation_id = relation_id
        if datatype is not None: self.datatype = datatype

        self.version = latest_version()
        SESSION.add(self)
        SESSION.flush()


        
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

        params = ('key','value','subkey','number','datatype',)
                  #'int_value','string_value','datetime_value','relation_id')
                  

        vals = ((x,getattr(self,x)) for x in params)
        strs = ("%s=%s" % (key, ("'%s'" % val if isinstance(val,basestring) else '%s'%str(val))) for key, val in vals)

        s = "%s(%s)" % (self.__class__.__name__, ','.join(strs))

        return s

    def __str__(self):

        params = ('key','number','subkey','datatype',)

        val = "%s.%s %s" % (self.entity.name, '|'.join([str(getattr(self, param)) for param in params]), str(self.value))
        return val

    @property
    def is_relation(self):
        return self.datatype == 'relation'
    
    def getValueType(self, value=None):
        if value == None:
            if self.datatype == None:
                valtype = "string"
            else:
                valtype = self.datatype
        else:
            valtype = self.get_type(value)
        
        return valtype + "_value"

    @property
    def keytuple(self):
        return (self.key, self.number, self.subkey)

    @classmethod
    def get_type(self, value):

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
            self.datatype = self.get_type(value)

        setattr(self, self.getValueType(value), value)



    value = property(_get_value, _set_value)

    def delete(self):
        ### TODO this seems like a hack
        
        try:
            SESSION.delete(self)
        except InvalidRequestError:
            pass #SESSION.expunge(self)

    @classmethod
    def queryarg(cls, key=None, value=(), subkey=(), number=()):

        args = []
        
        if key:
            args.append(Attribute.key==key)
            
        if number is not ():
            args.append(Attribute.number==number)

        if subkey is not ():
            args.append(Attribute.subkey==subkey)

        if value is not ():
            valtype = Attribute.get_type(value) + '_value'
            if valtype == 'relation_value':

                # get entity_id from Drivers too
                if hasattr(value, 'entity'):
                    e = value.entity
                else:
                    e = value
                    
                args.append(getattr(Attribute, 'relation_id') == e.entity_id)
                
            else:
                args.append(getattr(Attribute, valtype) == value)

        return and_(*args)

class Entity(object):
    """
    The base object that can be stored and managed in clusto.

    An entity can have a name, type, and attributes.

    An Entity's functionality is augmented by Drivers which act as proxies for
    interacting with an Entity and its Attributes.
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

        self.version = latest_version()
        SESSION.add(self)
        SESSION.flush()
        
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
            
        return str(self.name)
            

    def add_attr(self, *args, **kwargs):

        return Attribute(self, *args, **kwargs)
        
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
    



mapper(ClustoVersioning, CLUSTO_VERSIONING)
mapper(Attribute, ATTR_TABLE,
       properties = {'relation_value': relation(Entity, lazy=True, 
                                                primaryjoin=ATTR_TABLE.c.relation_id==ENTITY_TABLE.c.entity_id,
                                                uselist=False,
                                                passive_updates=False)})


## might be better to make the relationships here dynamic_loaders in the long
## term.
mapper(Entity, ENTITY_TABLE,
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


