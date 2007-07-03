from schema import *
#from sqlalchemyhelpers import _AssociationMultiDict

class Thing(object):

    __metaclass__ = ClustoThing

    metaattrs = {'clustotype': 'thing'}

    # I can't get multivalued dict like behavior working quite right
    # and I'm not entirely sure that's the best interface anyway.
    #attrs = association_proxy('_attrs', 'value',
    #                          proxy_factory=_AssociationMultiDict)
    
    def __init__(self, name, thingtype=None):
        
        self.name = name


        if thingtype:
            self.addAttr('clustotype', thingtype)

        self.updateAttrs(self.metaattrs)


    def __new__(self, *args, **kwargs):

        newthing = super(Thing, self).__new__(self, *args, **kwargs)
        newthing._setProperClass()
        return newthing

    def _setProperClass(self):
        s=set(self.metaattrs.items())
        possible_classes = [ i for i in driverlist
                             if (s.issubset(set(i.metaattrs.items())))]

        
        # sort the possible_classes so that the least specific one is used
        # (the one with the fewest metaattrs)
        # I'm not sure if this is the most correct behaviour
        possible_classes.sort(cmp=lambda x,y: cmp(len(x.metaattrs),
                                                  len(y.metaattrs)),)
                              
        #sys.stderr.write('setPropClass: ' + str(possible_classes) + '\n')
        self.__class__ = possible_classes.pop(0)

        
    def a__str__(self):

        out = ["%s.type %s\n" % (self.name, self._attrs['clustotype'])]
        for attr in self._attrs:
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
            #newthing.__class__ = driverlist[newthing.attrs['driver']]
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
        
    @classmethod
    def ThingByName(self,name):

        """take a name of a thing and return a thing object"""
        thing=Thing.select(Thing.c.name==name)[0]

        return(thing)

    def getByName(self, name):
        pass

    @classmethod
    def query(self, **queryparams):
        """
        This function lets you search for Things.

        
        
        """

        pass
        

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
        del(attr)

    def delAttrs(self, key):
        """
        Delete all attributes with the given key
        """
        attrlist = filter(lambda x: x.key == key, self._attrs)

        for i in attrlist:
            del(i)
        
        
    def getAttrs(self, keys=None, asdict=False):
        """
        Returns a list of the key value pairs of the attributes associated
        with this Thing.

        When keys is specified it will only return those keys, otherwise it'll
        return all attributes.
        
        If asdict is True then it'll return a dictionary where the values are
        all lists.  
        """

        if keys:
            attrlist = [(i.key, i.value)
                        for i in self._attrs if i.key in keys]
            
        else:
            attrlist = [(i.key, i.value) for i in self._attrs]


        if asdict:
            attrlist = AttributeDict(attrlist)
            
        return attrlist

    def getAttr(self, key, justone=True):
        """
        returns the first value of a given key.

        if justone is False then return all values for the given key.
        """
        
        attrlist = filter(lambda x: x.key == key, self._attrs)

        return justone and attrlist[0].value or [a.value for a in attrlist]


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
        attr.value = newval
        
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
            
            
