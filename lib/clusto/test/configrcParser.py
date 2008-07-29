import testbase
import unittest
import libDigg

from drivers import *
from schema import *

class ParseConfigRc(file):

    def __init__(self, file):
        self.file = file

    def parse(self):

        """parse a configrc style file and return a dictionary of dictionarys and a dictionary with the relations"""

        f = libDigg.fopen (self.file,"r")

        rellist = {}
        objects = {}
        for line in f:

            if line == "\n":
                continue
            sline = line.split(' ',1)
            key = sline[0]
            value = sline[1].rstrip("\n\r")
            ksplit = key.split('.',1)
            object = ksplit[0]
            mkey = ksplit[1]
            try:
                list = objects.setdefault(object, {})[mkey]
                list.append(value)
                objects.setdefault(object, {})[mkey] = list
            except KeyError:
                # I bet there is a better way to do this
                list = [ ]
                list.append(value)
                objects.setdefault(object, {})[mkey] = list
                list = [ ]

            # yes, it does this every time for now
            # note that this is not a list like the other stuff

            objects.setdefault(object, {})['name'] = ksplit[0]

        f.close()
        
        objects.setdefault(object, {})['name'] = ksplit[0]

        # put all of the relations into a hash
        # and test to see if they all make sense
        # I have tested it somewhat, but this might fail if
        # a db object has more than one 'rel' set but not all of them
        # have corresponding rels - ie this only checks that for
        # a relation there is at least one rel back on the object it refers
        # to, not that is necessarily refers back to itself

        for i in objects.keys():
            try:
                rel = objects.setdefault(i)['rel']
                rellist[i] = rel  
            except KeyError:
                continue

        # check and make sure all rels match

        for li in rellist.values():
            for i in li:
                if rellist.has_key(i):
                    # surely a better way to do this
                    pass
                else:
                    print "no key %s" % i
                    sys.exit()
                
        return(objects,rellist)

class UseDb:

    def __init__(self,objects,rellist):
        metadata.connect('sqlite:///clusto.sql')    
        self.objects = objects
        self.rellist = rellist
        metadata.engine.echo = False
        metadata.create_all()

    def insertThing(self):
        objects = self.objects 
        for key in objects.keys():
            try:
                name = objects.setdefault(key)['name']
            except KeyError:
                print "%s does not have 'name' set" % key
                sys.exit()
            try:
                list = objects.setdefault(key)['type']
                type = list[0]
            except KeyError:
                print "%s does not have 'type' set" % key
                sys.exit()
            if type == "server":
                thing = Server(name)
            else:
                thing = Thing(name,type)

            obj = objects[name]

            # remember, the values of k come in as a list
            # except for the "name". silly hack
            #FIXME
            # also, we expect there to be one or more items for relations (rels)
                
            for k in obj.keys():

                if k == "name":
                    item = obj[k]
                else:
                    litem = obj[k]
                    item = litem[0]

                thing.attrs[k] = item

        ctx.current.flush()
        
    def insertRel(self):
        """take the rellist list and make the actual connections via objects"""

        for k,v in self.rellist.items():
            
            rel1=Thing.ThingByName(k)

            for item in v:
                rel2=Thing.ThingByName(item)
                rel1.connect(rel2)
        
        ctx.current.flush()

    def dropDatabase(self):
        
        """drops the database"""
        metadata.dispose()

if __name__ == '__main__':

    file = "configrc.reference"
    parsedfile=ParseConfigRc(file)

    (objects,rellist) = parsedfile.parse()

    db = UseDb(objects, rellist)
    db.insertThing()
    db.insertRel()
