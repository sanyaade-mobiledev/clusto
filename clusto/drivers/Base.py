from clusto.schema import *

    
class Thing(object):
    """
    Anything
    """
    __metaclass__ = ClustoThing

    meta_attrs = {}

    required_attrs = ()
    
    # I can't get multivalued dict like behavior working quite right
    # and I'm not entirely sure that's the best interface anyway.
    #attrs = association_proxy('_attrs', 'value',
    #                          proxy_factory=_AssociationMultiDict)
    
    def __init__(self, name, *args, **kwargs):
        
        self.name = name


        #if thingtype:
        #    self.addAttr('clustotype', thingtype)
        if len(self.required_attrs) != (len(args) + len(kwargs)):
            raise TypeError(self.__class__.__name__ +
                            "() wrong number of arguments given.")
        

        reqattrs = list(self.required_attrs)

        for arg in kwargs:
            if arg in reqattrs:
                self.addAttr(arg, kwargs[arg])
                reqattrs.remove(arg)

        for arg in args:
            self.addAttr(reqattrs.pop(0), arg)


        
        for i in reversed(self.__class__.mro()):
            if hasattr(i, 'meta_attrs'):
                self.updateAttrs(i.meta_attrs, replaceAttrs=False)

        if hasattr(self, 'setup'):
            self.setup()
            


    def __new__(cls, *args, **kwargs):

        newthing = super(Thing, cls).__new__(cls, *args, **kwargs)
        #newthing._setProperClass()
        return newthing

    def __eq__(self, otherthing):
        """
        Am I the same as the Other Thing.
        """

        ## each Thing must have a unique name so I'll just compare those

        return self.name == otherthing.name

    def _setProperClass(self):
        """
        Set the class for the proper object to the best suited driver
        """

        attrset = set(self.getAttrs())
        possible_classes = [ DRIVERLIST[i] for i in DRIVERLIST
                             if (attrset.issuperset(set(DRIVERLIST[i]._all_meta_attrs.items())))]


        # sort the possible_classes so that the most specific one is used
        # (the one with the most matching meta_attrs)
        # I'm not sure if this is the most correct behaviour
        possible_classes.sort(cmp=lambda x, y: cmp(x._all_meta_attrs.items(),
                                                   y._all_meta_attrs.items()))
                              

        self.__class__ = possible_classes.pop(-1)

        
    def __str__(self):

        out = []
        for attr in self._attrs:
            out.append("%s.%s %s" % (self.name, attr.key, attr.value))

        for con in self.connections:
            out.append("%s._rel %s" % (self.name, con.name))

        if not self.hasAttr('clustotype'):
            out.append("%s.clustotype thing" % (self.name))
            
        return '\n'.join(out)


    
    ##
    # Connection related functions
    ##
    def _get_connections(self):
        """
        Returns a list of things this Thing is connected to.
        """
        connlist = []
        
        ta = ThingAssociation.select(or_(ThingAssociation.c.thing_name1==self.name,
                                         ThingAssociation.c.thing_name2==self.name))

        for i in ta:
            itemname = (i.thing_name1 == self.name) \
                       and i.thing_name2 or i.thing_name1
            
            newthing = Thing.selectfirst_by(name=itemname)

            ## this is a crude brute force method of getting Things in the
            ## form of their respective driver objects
            ## I think I can just change __class__ for the object to make it
            ## work
            #newthing = driverlist[newthing.attrs['driver']].selectfirst_by(name=itemname)
            #newthing.__class__ = driverlist[newthing.attrs['driver']]
            #newthing._setProperClass()
            connlist.append(newthing)

        return connlist

    
    connections = property(_get_connections)
        
    def disconnect(self, thing):
        """
        Disconnect a given Thing from self
        """

        conn = ThingAssociation.select(or_(ThingAssociation.c.thing_name1==self.name,
                                           ThingAssociation.c.thing_name2==self.name))

        for i in conn:
            i.delete()


    def connect(self, thing, force=False):
        """
        Connect a given Thing to self

        Normally tests if self canConnectTo the given thing.

        if force is set to True then the connectability test is skipped
        """

        if not force:
            if not (self.canConnectTo(thing) and thing.canConnectTo(self)):
                raise ConnectionException("%s and %s are not connectable" %
                                          (self.name, thing.name))
            
        ta = ThingAssociation(self, thing)

        
    def canConnectTo(self, thing):
        """
        Can this Thing connect to the given Thing. returns a boolean
        """

        return True
        
    ##
    # Attribute related functions
    #

    def addAttr(self, key, value):
        """
        Add an attribute (key/value pair) to this Thing.

        Attribute keys can have multiple values.
        """
        self._attrs.append(Attribute(key, value))

    def addAttrs(self, attrlist):
        """
        Add a list or dict of attributes to this Thing.

        Takes in a list of the form [(key1, value1), (key2, value2), ...] or
        a dictionary.  If a dictionary in the key has a value which is a list
        then that is recorded as multiple attrubutes
        (i.e. (key, value1), (key, value2), (key, value3) ...
        """
        
        if isinstance(attrlist, dict):
            attrlist = attrlist.items()
            
        for attr in attrlist:

            if isinstance(attr[1], list):
                for value in attr[1]:
                    self.addAttr(attr[0], value)
            else:
                self.addAttr(attr[0], attr[1])


    def delAttr(self, key, value):
        """
        Delete the attribute matching the given key/value pair
        """
        attr = filter(lambda x: x.key == key and x.value == value, self._attrs)
        for i in attr:
            self._attrs.remove(i)

    def delAttrs(self, key):
        """
        Delete all attributes with the given key
        """
        attrlist = filter(lambda x: x.key == key, self._attrs)

        for i in attrlist:
            self._attrs.remove(i)
            
        

        
    def getAttrs(self, keys=None, asdict=False,
                 onlyvalues=False, sort=False):
        """
        Returns a list of the key value pairs of the attributes associated
        with this Thing.

        When keys is specified it will only return those keys, otherwise it'll
        return all attributes.
        
        If asdict is True then it'll return a dictionary where the values are
        all lists.

        If sorted is True then a simple sort() will be called on the on the
        list before returning
        """

        attrs = self._attrs

        # return just value or key/value tuple
        rettype = onlyvalues and (lambda x: x.value) \
                  or (lambda x: (x.key, x.value))
        if keys:
            attrlist = [rettype(i) for i in attrs if i.key in keys]
        else:
            attrlist = [rettype(i) for i in attrs]
            
        attrlist.sort()

        if asdict and not onlyvalues:
            attrlist = AttributeDict(attrlist)
        
        return attrlist

    def getAttr(self, key, justone=True):
        """
        returns the first value of a given key.

        if justone is False then return all values for the given key.
        """
        
        attrlist = filter(lambda x: x.key == key, self._attrs)

        return justone and attrlist[0].value or [a.value for a in attrlist]

    def hasAttr(self, key, value=None):

        if value:
            attrlist = filter(lambda x: x.key == key and x.value == value, self._attrs)
        else:
            attrlist = filter(lambda x: x.key == key, self._attrs)

        return attrlist and True or False

    def setAttrs(self, key, valuelist):
        """
        Set the given key to the given valuelist.

        This will first clear all the attributes with the given key then
        add attributes with the key/value pairs where the value comes from
        the valuelist.
        """

        self.delAttrs(key)
        self.addAttrs(((key,v) for v in valuelist))

    def setAttr(self, keyval, newval):
        """
        Set a given key value pair with a new value.

        keyval is a (key, value) tuple
        """
        # this is kind of innefficient

        attr = filter(lambda x: x.key == keyval[0] and x.value == keyval[1],
                      self._attrs)

        if not attr:
            self.addAttr(keyval, newval)
        else:
            attr[0].value = newval
        
    def updateAttrs(self, attrdict, replaceAttrs=True):
        """
        Update attributes from a given dict.

        If replaceAttrs is True then Attributes that have keys from attrdict
        get removed and replaced with values from attrdict.

        If a value from attrdict is a list then the elements from that list
        get used to construct multiple key/value pairs where the key is the
        key for that value list and the value is an element of the value list.
        
        """

        if replaceAttrs:
            for newkey in attrdict:
                self.delAttrs(newkey)
            
        self.addAttrs(attrdict.items())
            


    ##
    # Matching and searching functions
    #
    def getConnectedMatching(self, matchdict, exact=False):
        """
        Get the objects this Thing is directly connected to that match the
        given criteria.

        matchdict should be AttributeDict compatible
        """

        return [athing for athing in self.connections
                if athing.isMatch(matchdict, exact=exact)]

    def isOfType(self, something):
        """
        Is this thing of the same type as the Thing/Driver given
        """

        return something.isMatch(AttributeDict(something.all_meta_attrs))

    def isMatch(self, matchdict, exact=False, completekeys=False):
        """
        Does this Thing match the given matchdict.

        if exact is True then the matchdict has to exactly match all the
        attributes.

        if completekeys is True then the complete set of values for the
        keys given in matchdict have to match this Thing.  This thing may
        still have other keys that aren't specified in matchdict.
        """
            
        attrs = self.getAttrs()

        # if clustoname is included in the matchdict then the name
        # should be included as an element of the search
        if 'clustoname' in matchdict.keys():
            attrs.append(('clustoname', self.name))

        for item in matchdict.items():
            try:
                attrs.remove(item)
            except:
                return False

        if exact:
            return (len(attrs) == 0)

        if completekeys:
            attrdict = AttributeDict(attrs)
            return not bool(set(matchdict.keys()) & set(attrdict.keys()))

        return True


    connector = False

    def searchConnections(self, matchargs=(), nonmatchargs=(),
                          alreadySearched=None):
        """
        Search for OtherThings connected to this Thing.

        This is a complicated function.  It takes in two arguments.

        matchargs - a list of dictionaries with key/values that get past
                    to each connected object's isMatch function

        nonmatchargs - same format as matchargs but Things matching these
                       matching dictionaries are discarded

        Effectively the elements of these lists are OR'd together.

        Things that set the member variable 'connector' to True get searched
        recursively.
        """

        if not alreadySearched:
            alreadySearched = set([self.name])

        result = []

        for item in self.connections:

            if item.name in alreadySearched:
                continue
            else:
                alreadySearched.add(item.name)

            # an empty matchargs should match everything
            if matchargs == ():
                result.append(item)
                if item.connector:
                    result.extend(item.searchConnections(matchargs,
                                                         nonmatchargs,
                                                         alreadySearched))
                    
            for args in matchargs:

                if item.isMatch(**args):
                    result.append(item)

                    # I'm not sure if this behaviour here is correct
                    # The idea is that if I found a match I shouldn't
                    # traverse up the connector.
                    # Like if I was searching for a specific NIC connected to
                    # a server then I woudn't want to travers up the NIC
                    # to the also search the IPs connected to it.
                    continue 
                
                if item.connector:
                    result.extend(item.searchConnections(matchargs,
                                                         nonmatchargs,
                                                         alreadySearched))


        for args in nonmatchargs:
            for item in result:
                if item.isMatch(**args):
                    result.remove(item)
        

        return result

    def connectedByType(self, somedriver, invert=False):
        """
        Given a driver get Things connected to self that match that driver.
        """

        searchargs = {invert and 'nonmatchargs' or 'matchargs':
                      [{'matchdict':
                        AttributeDict(somedriver.all_meta_attrs)}]}
        
        retval = self.searchConnections(**searchargs)

        return retval

    def query(self, *args, **kwargs):
        pass

#class Resource(Thing):
#    meta_attrs = {'clustotype' : 'resource' }
    


class Part(Thing):

    meta_attrs = {'clustotype' : 'part' }

    connector = True
