
from clusto.drivers import DRIVERLIST, TYPELIST, Driver, ClustoMeta
from clusto.schema import SESSION, METADATA, Entity, Attribute, VERSION
from sqlalchemy import and_, or_, literal, create_engine
from sqlalchemy.exceptions import InvalidRequestError

import clusto.drivers
driverlist = DRIVERLIST
typelist = TYPELIST


def connect(dsn):
    """
    Connect to a given Clusto datastore.

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
    """
    Initialize a clusto database.
    """
    METADATA.create_all(METADATA.bind)
    c = ClustoMeta()
    
    flush()

def flush():
    """
    Flush changes made to clusto objects to the database.
    """
    SESSION.flush()
    SESSION.commit()


def clear():
    """
    Clear the changes made to objects in the current session.
    """
    
    SESSION.clear()
    #SESSION.remove()


def getDriver(entity, ignoreDriverColumn=False):
    """
    Return the driver to use for a given entity
    """

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
    """
    Rename an Entity from oldname to newname.
    """

    old = getByName(oldname)

    old.name = newname

    flush()


## unconverted functions
def disconnect():
    SESSION.close()
    


def query(attrs=(), names=(), ofTypes=(), filterArgs=()):
    """
    Query clusto for objects matching the query parameters.

    Each argument accepts a list. Each element of the list is OR'd
    together.  If an element is a tuple then it's contents are anded
    during the query.

    attrs - attributes of a Thing
    names - name of a Thing
    ofTypes - driver classes of a Thing
    """

    
    queryarg = []
    hasattrs = False
    for clustoType in ofTypes:
        if isinstance(clustoType, list) or isinstance(clustoType, tuple):
            wherelist = []
            for sometype in clustoType:
                if sometype.all_meta_attrs == Thing.all_meta_attrs:
                    # everything is a Thing so it'll match unconditionally
                    wherelist.append(literal('true') == literal('true'))
                    
                else:
                    hasattrs=True # ugly hack to account for Things which have no attrs
                    wherelist.extend([and_(Attribute.c.key == attr[0],
                                           Attribute.c.value == attr[1])
                                      for attr in sometype.all_meta_attrs])
            queryarg.append(and_(*wherelist))
        else:
            if clustoType.all_meta_attrs == Thing.all_meta_attrs:
                # everything is a Thing so it'll match unconditionally
                queryarg.append(literal('true') == literal('true'))
                #continue
            else:
                hasattrs = True # ugly hack to account for Things which have no attrs
                queryarg.extend([and_(Attribute.c.key == attr[0],
                                      Attribute.c.value == attr[1])
                                 for attr in clustoType.all_meta_attrs])

    for name in names:
        if isinstance(name, list) or isinstance(name, tuple):
            raise TypeError("the names parameter cannot contain lists or tuples")
        else:
            queryarg.append(Thing.c.name == name)

    for attr in attrs:
        if isinstance(attr, list) or isinstance(attr, tuple):
            wherelist = []
            for someattr in attr:
                if not someattr:
                    continue
                else:
                    hasattrs = True # ugly hack to account for Things which have no attrs
                    wherelist.extend([and_(Attribute.c.key == a[0],
                                           Attribute.c.value == a[1])
                                      for a in attr])
            queryarg.append(and_(*wherelist))
        else:
            queryarg.append(and_(Attribute.c.key == attr[0],
                                 Attribute.c.value == attr[1]))

    if not queryarg:
        retval = Thing.query()
    elif hasattrs:
        retval = Thing.query.filter(and_(Thing.c.name == Attribute.c.thing_name, or_(*queryarg)))

    else:
        retval = Thing.query.filter(or_(*queryarg))

    return list(retval)
            

    
    

