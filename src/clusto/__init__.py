

from schema import *
from clusto.exceptions import *

from drivers import DRIVERLIST, TYPELIST, Driver, ClustoMeta
from sqlalchemy.exceptions import InvalidRequestError
from sqlalchemy import create_engine


import drivers

import threading
import logging

driverlist = DRIVERLIST
typelist = TYPELIST


def connect(dsn, echo=False):
    """Connect to a given Clusto datastore.

    Accepts a dsn string.

    e.g. mysql://user:pass@example.com/clustodb
    e.g. sqlite:///somefile.db

    @param dsn: the clusto database URI
    """
    SESSION.configure(bind=create_engine(dsn, echo=echo))

def checkDBcompatibility(dbver):

    if dbver == VERSION:
        return True

init_semaphore = threading.Semaphore()
def init_clusto():
    """Initialize a clusto database. """
    init_semaphore.acquire()
    METADATA.create_all(SESSION.bind)
    c = ClustoMeta()
    flush()
    init_semaphore.release()


def flush():
    """Flush changes made to clusto objects to the database."""

    SESSION.flush()
            


def clear():
    """Clear the changes made to objects in the current session. """

    SESSION.expunge_all()

def get_driver_name(name):
    "Return driver name given a name, Driver class, or Driver/Entity instance."

    if isinstance(name, str):
        if name in DRIVERLIST:
            return name
        else:
            raise NameError("driver name %s doesn't exist." % name)
    elif isinstance(name, type):
        return name._driver_name

    elif isinstance(name, Entity):
        return name.driver
    else:
        raise LookupError("Couldn't find driver name.")
    
def get_type_name(name):

    if isinstance(name, str):
        if name in TYPELIST:
            return name
        else:
            raise NameError("driver name %s doesn't exist." % name)

    elif isinstance(name, type):
        return name._clusto_type
    elif isinstance(name, Entity):
        return name.type
    else:
        raise LookupError("Couldn't find type name.")
        

def get_driver(entity):
    """Return the driver to use for a given entity """

    if entity.driver in DRIVERLIST:
        return DRIVERLIST[entity.driver]

    return Driver

def get_entities(names=(), clusto_types=(), clusto_drivers=(), attrs=()):
    """Get entities matching the given criteria

    @param names: list of names to match
    @type names: list of strings
    
    @param clustotypes: list of clustotypes to match
    @param clustotypes: list of strings or Drivers

    @param clustodrivers: list of clustodrives to get
    @type clustodrives: list of strings or Drivers

    @param attrs: list of attribute parameters
    @type attrs: list of dictionaries with the following 
                 valid keys: key, number, subkey, value
    """
    
    query = Entity.query()

    if names:
        query = query.filter(Entity.name.in_(names))

    if clusto_types:
        ctl = [get_type_name(n) for n in clusto_types]
        query = query.filter(Entity.type.in_(ctl))

    if clusto_drivers:
        cdl = [get_driver_name(n) for n in clusto_drivers]
        query = query.filter(Entity.driver.in_(cdl))

    if attrs:
        query = query.filter(Attribute.entity_id==Entity.entity_id)

        query = query.filter(or_(*[Attribute.queryarg(**args) 
                                   for args in attrs]))
        

    return [Driver(entity) for entity in query.all()]

    
def get_by_name(name):
    try:
        entity = Entity.query().filter_by(name=name).one()

        retval = Driver(entity)
            
        return retval
    except InvalidRequestError:
        raise LookupError(name + " does not exist.")

get_by_attr = drivers.base.Driver.get_by_attr

def get_or_create(name, driver):
    try:
        obj = get_by_name(name)
    except LookupError:
        obj = driver(name)
        logging.info('Created %s' % obj)
    return obj

              
def rename(oldname, newname):
    """Rename an Entity from oldname to newname.

    THIS CAN CAUSE PROBLEMS IF NOT USED CAREFULLY AND IN ISOLATION FROM OTHER
    ACTIONS.
    """

    old = get_by_name(oldname)

    try:
        begin_transaction()
        
        new = get_driver(old.entity)(newname)

        for attr in old.attrs(ignore_hidden=False):
            new.add_attr(key=attr.key,
                         number=attr.number,
                         subkey=attr.subkey,
                         value=attr.value)

        for ref in old.references(ignore_hidden=False):
            ref.delete()
            ref.entity.add_attr(key=ref.key,
                                number=ref.number,
                                subkey=ref.subkey,
                                value=new)

        for counter in SESSION.query(Counter).filter(Counter.entity==old.entity):
            counter.entity = new.entity
            
        old.entity.delete()
        commit()
    except Exception, x:
        rollback_transaction()
        raise x

def get_latest_version_number():
    "Return the latest version number"

    s = SESSION()

    val = s.execute(latest_version()).fetchone()[0]
    return val


def _check_transaction_counter():
    tl = SESSION()

    if not hasattr(tl, 'TRANSACTIONCOUNTER'):
        raise TransactionException("No transaction counter.  Outside of a transaction.")
    
    if tl.TRANSACTIONCOUNTER < 0:
        raise TransactionException("Negative transaction counter!  SHOULD NEVER HAPPEN!")

def _init_transaction_counter():

    tl = SESSION()
    if not hasattr(tl, 'TRANSACTIONCOUNTER'):
        tl.TRANSACTIONCOUNTER = 0
    else:
        raise TransactionException("Transaction counter already initialized.")
    
def _inc_transaction_counter():
    _check_transaction_counter()

    tl = SESSION()
    
    tl.TRANSACTIONCOUNTER += 1
    
def _dec_transaction_counter():

    _check_transaction_counter()
    
    tl = SESSION()
    
    tl.TRANSACTIONCOUNTER -= 1

    if tl.TRANSACTIONCOUNTER == 0:
        del tl.TRANSACTIONCOUNTER

    
def begin_transaction():
    """Start a transaction

    If already in a transaction start a savepoint transaction.

    If allow_nested is False then an exception will be raised if we're already
    in a transaction.
    """
    
    if SESSION.is_active:
        _inc_transaction_counter()
        return None
    else:
        _init_transaction_counter()
        _inc_transaction_counter()
        return SESSION.begin()

def rollback_transaction():
    """Rollback a transaction"""

    tl = SESSION()
    _check_transaction_counter()
    if SESSION.is_active:
        SESSION.rollback()
        _dec_transaction_counter()
    
    
def commit():
    """Commit changes to the datastore"""

    _check_transaction_counter()
    tl = SESSION()
    if SESSION.is_active:
        if tl.TRANSACTIONCOUNTER == 1:
            SESSION.commit()
        _dec_transaction_counter()
        flush()
            

def disconnect():
    SESSION.close()

def delete_entity(entity):
    """Delete an entity and all it's attributes and references"""
    try:
        begin_transaction()
        entity.delete()
        commit()
    except Exception, x:
        rollback_transaction()
        raise x
    

    
