



from sqlalchemy import *
from sqlalchemy.ext.sessioncontext import SessionContext
from sqlalchemy.ext.assignmapper import assign_mapper
from sqlalchemy.ext.associationproxy import association_proxy


#from schema import *
#from drivers import *

metadata = DynamicMetaData()

ctx = SessionContext(create_session)

thing_table = Table('things', metadata,
                    Column('name', String(128), primary_key=True),
                    #Column('thingtype', String(128)),
                    mysql_engine='InnoDB'
                    )

class Thing(object):

    def __init__(self, name, thingtype=None):

        self.name = name

assign_mapper(ctx, Thing, thing_table)

metadata.connect('sqlite:///:memory:')
metadata.create_all()


t=Thing('foo', 'bar')
