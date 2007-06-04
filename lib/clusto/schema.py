"""
Clusto schema

"""

from sqlalchemy import *
from sqlalchemy.ext.sessioncontext import SessionContext
from sqlalchemy.ext.assignmapper import assign_mapper

import sys
# session context


metadata = DynamicMetaData()


ctx = SessionContext(create_session)

thing_table = Table('things', metadata,
                    Column('name', String(128), primary_key=True),
                    Column('thingtype', String(128)),
                    mysql_engine='InnoDB'
                    )

attr_table = Table('thing_attrs', metadata,
                   Column('attr_id', Integer, primary_key=True),
                   Column('thing_name', String(128), ForeignKey('things.name', ondelete="CASCADE", onupdate="CASCADE")),
                   Column('name', String(1024)),
                   Column('value', String),
                   mysql_engine='InnoDB'
                   )

thingthing_table = Table('thing_thing', metadata,
                         Column('thing_name1', String(128), ForeignKey('things.name', ondelete="CASCADE", onupdate="CASCADE"), primary_key=True),
                         Column('thing_name2', String(128), ForeignKey('things.name', ondelete="CASCADE", onupdate="CASCADE"), primary_key=True),
                         mysql_engine='InnoDB'
                         )


class Attribute(object):
    def __init__(self, name, value, thing_name=None):
        self.name = name
        self.value = value

        if thing_name:
            self.thing_name = thing_name

    def __str__(self):
        return "thingname: %s, keyname: %s, value: %s" % (self.thing_name,
                                                          self.name,
                                                          self.value)

assign_mapper(ctx, Attribute, attr_table)

class AttributeDict(dict):
    def __init__(self, attrlist):
        self.attrlist = attrlist
        self.attrdict = {}

        for i in attrlist:
            self[i.name] = i.value
            self.attrdict[i.name] = i
            
    def __setitem__(self, name, value):
        
        if name in self.attrdict:
            self.attrdict[name].value = value
        else:
            newattr = Attribute(name,value)
            self.append(newattr)
            
    def append(self, item):
        
        self.attrlist.append(item)
        dict.__setitem__(self, item.name, item.value)        
        self.attrdict[item.name] = item
        
    def __iter__(self):
        return self.attrlist.itervalues()


driverlist = {}

class ClustoThing(type):
    def __init__(cls, name, bases, dct):

        cls.drivername = name

        if hasattr(cls, 'clustotype'):
            s = select([thing_table],
                       thing_table.c.thingtype==cls.clustotype
                       ).alias(cls.clustotype+'alias')


            driverlist[cls.drivername] = cls
        else:
            s = thing_table

        
        assign_mapper(ctx, cls, s, properties={
            'attrslist' : relation(Attribute, lazy=False,
                                   cascade='all, delete-orphan',),

                })

        
        super(ClustoThing, cls).__init__(name, bases, dct)
        


class Thing(object):

    __metaclass__ = ClustoThing

    metaattrs = {}
    
    def __init__(self, name, thingtype):
        self.name = name
        self.thingtype = thingtype

        #self.attrslist = []
        self.attrs = AttributeDict(self.attrslist)
        self.attrs['driver'] = self.drivername

        self.attrs.update(self.metaattrs)

    def _get_connections(self):

        connlist = []
        
        ta = ThingAssociation.select(or_(ThingAssociation.c.thing_name1==self.name,
                                         ThingAssociation.c.thing_name2==self.name))

        for i in ta:
            itemname = (i.thing_name1 == self.name) and i.thing_name2 or i.thing_name1
            connlist.append(Thing.selectfirst_by(name=itemname))

        return connlist


    connections = property(_get_connections)
    
    def disconnect(self, thing):

        conn = ThingAssociation.select(or_(ThingAssociation.c.thing_name1==self.name,
                                           ThingAssociation.c.thing_name2==self.name))

        for i in conn:
            i.delete()

        ctx.current.flush()
        

    def connect(self, thing):

        ta = ThingAssociation(self, thing)
        

        


    
class ThingAssociation(object):
    def __init__(self, thing1, thing2):
        self.thing_name1 = thing1.name
        self.thing_name2 = thing2.name


assign_mapper(ctx, ThingAssociation, thingthing_table)

