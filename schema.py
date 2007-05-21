"""
Clusto schema

"""

from sqlalchemy import *
from sqlalchemy.ext.sessioncontext import SessionContext
from sqlalchemy.ext.assignmapper import assign_mapper

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
    def __init__(self, name, value):
        self.name = name
        self.value = value

mapper(Attribute, attr_table)

class Thing(object):

    def __init__(self, name, thingtype):
        self.name = name
        self.thingtype = thingtype

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

assign_mapper(ctx, Thing, thing_table, properties={
    'attrs' : relation(Attribute, lazy=False, cascade='all, delete-orphan'),
    })

assign_mapper(ctx, ThingAssociation, thingthing_table)

