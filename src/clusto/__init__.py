

from schema import *


from drivers import DRIVERLIST, TYPELIST, Driver, ClustoMeta
from sqlalchemy.exceptions import InvalidRequestError
from sqlalchemy import create_engine


import drivers
driverlist = DRIVERLIST
typelist = TYPELIST


def connect(dsn):
    """Connect to a given Clusto datastore.

    Accepts a dsn string.

    e.g. mysql://user:pass@example.com/clustodb
    e.g. sqlite:///somefile.db

    @param dsn: the clusto database URI
    """
    METADATA.bind = create_engine(dsn)

def checkDBcompatibility(dbver):

    if dbver == VERSION:
        return True

def initclusto():
    """Initialize a clusto database. """
    METADATA.create_all(METADATA.bind)
    c = ClustoMeta()

    flush()


def flush():
    """Flush changes made to clusto objects to the database."""

    SESSION.flush()
    SESSION.commit()
	


def clear():
    """Clear the changes made to objects in the current session. """
    
    SESSION.clear()
    #SESSION.remove()


def getDriver(entity, ignoreDriverColumn=False):
    """Return the driver to use for a given entity """

    if not ignoreDriverColumn:
        if entity.driver in DRIVERLIST:
            return DRIVERLIST[entity.driver]

    return Driver

def get(name=None, type=None, attrs=None):
    pass
    
def getByName(name):
    try:
        entity = SESSION.query(Entity).filter_by(name=name).one()

        #klass = getDriver(entity)
        #retval = klass(entity=entity)

        retval = Driver(entity)
            
        return retval
    except InvalidRequestError:
        raise LookupError(name + " does not exist.")


def rename(oldname, newname):
    """Rename an Entity from oldname to newname.

    THIS CAN CAUSE PROBLEMS IF NOT USED CAREFULLY AND IN ISOLATION FROM OTHER
    ACTIONS.
    """

    old = getByName(oldname)

    old.entity.name = newname

    flush()

def beginTransaction():
    """Start a transaction"""
    SESSION.begin(subtransactions=True)

def rollbackTransaction():
    """Rollback a transaction"""
    SESSION.rollback()
    SESSION.close()

def commit():
    """Commit changes to the datastore"""
    SESSION.commit()

## unconverted functions
def disconnect():
    SESSION.close()
