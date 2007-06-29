"""
Clusto schema

"""

from sqlalchemy import *
from sqlalchemy.ext.sessioncontext import SessionContext
from sqlalchemy.ext.assignmapper import assign_mapper
from sqlalchemy.ext.associationproxy import association_proxy

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


class ZAttributeDict(dict):
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
        
    #def __iter__(self):
    #    return self.attrlist.__iter__()


class AttributeDictNEW(dict):
    """
    My Attribute Dict
    """
    def append(self, item): 
         self[item.name] = item 
    def __iter__(self): 
         return self.itervalues()  
    def a__getitem__(self, item):
        sys.stderr.write(str(type(item)))
        return super(AttributeDictNEW, self).__getitem__(item.name)

    

driverlist = {}

class ClustoThing(type):
    def __init__(cls, name, bases, dct):

        cls.drivername = name
        driverlist[cls.drivername] = cls
        
        if hasattr(cls, 'clustotype'):
            s = select([thing_table],
                       thing_table.c.thingtype==cls.clustotype
                       ).alias(cls.clustotype+'alias')



        else:
            s = thing_table

        
        assign_mapper(ctx, cls, s, properties={
            '_attrs' : relation(Attribute, lazy=False,
                                cascade='all, delete-orphan',
                                collection_class=AttributeDictNEW),
            

                })

        
        super(ClustoThing, cls).__init__(name, bases, dct)


class Thing(object):

    __metaclass__ = ClustoThing

    metaattrs = {}

    attrs = association_proxy('_attrs', 'value')
    
    def __init__(self, name, thingtype):
        self.name = name
        self.thingtype = thingtype
        self.attrs['driver'] = self.drivername
        self.attrs.update(self.metaattrs)


    def __str__(self):

        out = ["%s.type %s\n" % (self.name, self.thingtype)]
        for attr in self.attrs:
            out.append("%s.%s %s\n" % (self.name, attr.name, attr.value))

        for con in self.connections:
            out.append("%s.rel %s" % (self.name, con.name))

        return ''.join(out)

    def _get_connections(self):

        connlist = []
        
        ta = ThingAssociation.select(or_(ThingAssociation.c.thing_name1==self.name,
                                         ThingAssociation.c.thing_name2==self.name))

        for i in ta:
            itemname = (i.thing_name1 == self.name) and i.thing_name2 or i.thing_name1
            newthing = Thing.selectfirst_by(name=itemname)

            ## this is a crude brute force method of getting Things in the
            ## form of their respective driver objects
            ## I think I can just change __class__ for the object to make it
            ## work
            #newthing = driverlist[newthing.attrs['driver']].selectfirst_by(name=itemname)
            connlist.append(newthing)

        return connlist


    connections = property(_get_connections)
    
    def disconnect(self, thing):

        conn = ThingAssociation.select(or_(ThingAssociation.c.thing_name1==self.name,
                                           ThingAssociation.c.thing_name2==self.name))

        for i in conn:
            i.delete()


    def connect(self, thing):

        ta = ThingAssociation(self, thing)
        
    def getAttrByName(self, name):

        thing=self.attrs[name]
        return(thing)

    @classmethod
    def ThingByName(self,name):
        
        """take a name of a thing and return a thing object"""
        thing=Thing.select(Thing.c.name==name)[0]

        return(thing)

    @classmethod
    def getAllThings(self):

        things=Thing.select()
        return(things)

    @classmethod
    def getThingsByKey(self,name):
        """takes a service name and returns server objects"""

        li=[]
        things=Thing.getAllThings()
        for i in things:
            try:
                if i.attrs[name]:
                    li.append(i)
            except:
                continue

        return(li)

    @classmethod
    def getAllServicesByValue(self,name):
        """takes a service name and returns server objects"""

        # broken at the moment
        li=[]
        things=Thing.getAllThings()
        for i in things:
            try:
                if i.attrs[name]:
                    li.append(i)
            except:
                continue

        return(li)

   
class ThingAssociation(object):
    def __init__(self, thing1, thing2):
        self.thing_name1 = thing1.name
        self.thing_name2 = thing2.name

assign_mapper(ctx, ThingAssociation, thingthing_table)

