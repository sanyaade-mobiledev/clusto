
from clusto.drivers.Base import Thing, Attribute
from clusto.schema import CTX, DRIVERLIST, METADATA
from sqlalchemy import and_, or_, literal
from sqlalchemy.exceptions import InvalidRequestError


driverlist = DRIVERLIST


def connect(dsn):
    METADATA.connect(dsn)

def flush():
    CTX.current.flush()


def getByName(name):
    try:
        return Thing.selectone(Thing.c.name == name)
    except InvalidRequestError:
        raise LookupError(name + " does not exist.")

def initclusto():
    METADATA.create_all()

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
        retval = Thing.select()
    elif hasattrs:
        retval = Thing.select(and_(Thing.c.name == Attribute.c.thing_name, or_(*queryarg)))

    else:
        retval = Thing.select(or_(*queryarg))

    return retval
            

def rename(oldname, newname):
    """
    Rename a Thing from oldname to newname.
    """

    old = getByName(oldname)

    new = Thing(newname)

    new.addAttrs(old.getAttrs())


    cons = old.searchConnections()

    for athing in cons:
        new.connect(athing)
        old.disconnect(athing)

    old.delete()

    
    

