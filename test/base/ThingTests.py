import unittest
from clusto.schema import METADATA, AttributeDict, THINGTHING_TABLE
from clusto.schema import ATTR_TABLE
import clusto
from clusto.drivers.Base import Thing, Part
from clusto.drivers.Servers import Server
from clusto.exceptions import *
import testbase

class TestThingSchema(testbase.ClustoTestBase):

    def data(self):
        t1 = Thing('foo1')
        t2 = Thing('foo2')

        t1.addAttr('attr1', 'one')

        t1.addAttr('attrN', 1)
        t1.addAttr('attrN', 2)
        t1.addAttr('attrN', 3)


        clusto.flush()


    def testThingObject(self):


        ts = Thing.query()

        self.assertEqual(2, len(list(ts)))


    def testThingWithSameName(self):
        """
        I shouldn't be able to have to Things with the same name
        """
        
        t1 = Thing('foo1')
        t2 = Thing('foo1')

        # maybe test for a more specific exception in the future
        self.assertRaises(Exception, clusto.flush)

    def testAddingAttributeToThing(self):

        tq = clusto.getByName('foo1')

        self.assertEqual('one',
                         tq.getAttr('attr1'))

    def testMulitpleValuesForSameAttrKeyTest(self):


        tq = clusto.getByName('foo1')

        values = tq.getAttr('attrN', justone=False)

        self.assertEqual(3, len(values))

        self.assertEqual([1,2,3], sorted(values))

class TestThingAttrs(testbase.ClustoTestBase):

    def data(self):
        t1 = Thing('foo1')

        t1.addAttr('attr1', 'one')

        t1 = Thing('t1')
        t1.addAttr('a', 1)
        t1.addAttr('a', 2)
        t1.addAttr('b', 3)
        
        clusto.flush()

        
    def testAttrOperations(self):

        t1 = clusto.getByName('foo1')
        
        t1.setAttrs('attr1', [1,2,3,4,5])

        clusto.flush()

        tq = clusto.getByName('foo1')
        
        values = tq.getAttr('attr1', justone=False)
        
        self.assertEqual(5, len(values))

        tq.delAttr('attr1', 2)

        clusto.flush()

        v = tq.getAttrs(['attr1'], onlyvalues=True)#, justone=False)
        
        self.assertEqual([1,3,4,5], sorted(v))
        
        tq.setAttrs('attr1', ['a','b'])

        clusto.flush()
        tq = clusto.getByName('foo1')

        values = tq.getAttr('attr1', justone=False)

        self.assertEqual(2, len(values))

        
    def testGetAttrs(self):

        t = clusto.getByName('t1')

        self.assert_(t.getAttrs(onlyvalues=True, sort=True) == [1, 2, 3])

    def testDelAttrs(self):


        self.assertEqual(len(list(ATTR_TABLE.select().execute())), 4)

        t1 = clusto.getByName('t1')
        t1.delete()
        clusto.flush()

        self.assertEqual(len(list(ATTR_TABLE.select().execute())), 1)




class TestThingConnections(testbase.ClustoTestBase):

    def data(self):
        t1 = Thing('foo1')
        t2 = Thing('foo2')
        t3 = Thing('foo3')
        
        t1.connect(t2)
        t1.connect(t3)

        clusto.flush()


    def testDelete(self):

        t2 = clusto.getByName('foo2')

        self.assertEqual(len(list(THINGTHING_TABLE.select().execute())),2)

        t2.delete()

        clusto.flush()

        self.assertEqual(len(list(THINGTHING_TABLE.select().execute())),1)
                
        self.assertRaises(LookupError, clusto.getByName, 'foo2')
        

        
    def testConnectingThings(self):
        
        t1 = clusto.getByName('foo1')
        t2 = clusto.getByName('foo2')
        t3 = clusto.getByName('foo3')
        
        self.assertEqual(2, len(t1.connections))
        self.assertEqual(1, len(t2.connections))
        self.assertEqual(1, len(t3.connections))

        self.assert_(t1 in t2.connections)

        self.assert_(t2 not in t3.connections)

        tt2 = clusto.getByName('foo2')
        tt3 = clusto.getByName('foo3')

        tt3.connect(tt2)
        clusto.flush()

        self.assert_(tt2 in tt3.connections)
        self.assert_(t1 in tt3.connections)

        tt2.disconnect(tt3)
        clusto.flush()
        
        self.assert_(tt2 not in tt3.connections)

    def testDoubleConnect(self):

        t1 = clusto.getByName('foo1')
        t2 = clusto.getByName('foo2')
        
        t1.connect(t2)
        t1.connect(t2)
        t1.connect(t2)
        t1.connect(t2)
        t1.connect(t2)

        clusto.flush()

        self.assertEqual(len(t1.connections), 2)

        self.assert_(t2 in t1.connections)

    def testSelfConnect(self):

        # shouldn't be able to connect to yourself
        t1 = clusto.getByName('foo1')

        self.assertRaises(ConnectionException, t1.connect, t1)
        

    def testDisconnect(self):

        t1 = clusto.getByName('foo1')
        t2 = clusto.getByName('foo2')
        
        self.assertEqual(len(list(THINGTHING_TABLE.select().execute())),2)

        t2.disconnect(t1)

        clusto.flush()
        
        self.assertEqual(len(list(THINGTHING_TABLE.select().execute())),1)

        

class TestThingSearching(testbase.ClustoTestBase):
    def data(self):

        t1 = Thing('t1')
        t2 = Thing('t2')

        t1.addAttr('a1', 1)
        t1.addAttr('a1', 3)
        t1.addAttr('a2', 2)
        clusto.flush()

        # Servers
        s1 = Server('s1')
        s2 = Server('s2')
        s3 = Server('s3')
        s4 = Server('s4')
        s5 = Server('s5')

        s2.addAttr('attr1', 1)
        s2.addAttr('attr2', 2)

        s4.addAttr('attr1', 1)
        s4.addAttr('attr2', 2)

        # part
        tp1 = Part('tp1')
        tp2 = Part('tp2')
        tp3 = Part('tp3')

        s1.connect(s2)
        #tp1.connect(s1)
        s1.connect(tp1)
        tp1.connect(s3)
        tp1.connect(tp2)
        tp2.connect(s4)
        

        clusto.flush()
        
    def testIsMatch(self):

        t1 = clusto.getByName('t1')
        
        self.assert_(not t1.isMatch(AttributeDict({'a1':1,
                                                   'a2':2}),
                                    exact=True))

        self.assert_(t1.isMatch(AttributeDict({'a1':1})))

        self.assert_(not t1.isMatch(AttributeDict({'a1':1}),
                                    completekeys=True))
        

        self.assert_(t1.isMatch(AttributeDict([('a1', 1),
                                               ('a1', 3)]),
                                completekeys=True))


    def testConnectionSearchForType(self):


        s1 = clusto.getByName('s1')

        result2 = s1.getConnectedByType(Server)

        compare = lambda x, y: cmp(x.name, y.name)

        
        expectedresult = map(clusto.getByName, ('s2', 's4', 's3'))

        self.assert_(sorted(result2, cmp=compare)
                     == sorted(expectedresult, cmp=compare))
        

    def testConnectionsSearch(self):

        tp = clusto.getByName('s1')

        
        query = [{'matchdict': AttributeDict({'attr1':'1',
                                              'attr2':'2'})}]
        
        result = tp.searchConnections(query)

        result.sort(cmp=lambda x, y: cmp(x.name, y.name))

        t2 = clusto.getByName('s2')
        t4 = clusto.getByName('s4')
        expectedresult = [t2, t4]
        expectedresult.sort(cmp=lambda x, y: cmp(x.name, y.name))
        
        print result    
        self.assert_(result == expectedresult)


    def testSearchBlank(self):

        # things
        t1 = Thing('tp')
        t2 = clusto.getByName('t2')
        t3 = Thing('t3')
        t4 = Thing('t4')
        t5 = Thing('t5')

        t2.addAttr('attr1', '1')
        t2.addAttr('attr2', '2')

        t4.addAttr('attr1', '1')
        t4.addAttr('attr2', '2')
        
        # part
        tp1 = clusto.getByName('tp1')
        tp2 = clusto.getByName('tp2')
        tp3 = clusto.getByName('tp3')

        t1.connect(t2)
        t1.connect(tp1)
        tp1.connect(t3)
        tp1.connect(tp2)
        tp2.connect(t4)
        
        clusto.flush()

        tp = clusto.getByName('tp')
        
        self.assert_(len(tp.searchConnections()) == 5)

        res = tp.searchConnections(nonmatchargs=[{'matchdict':
                                                  AttributeDict({'clustoname':
                                                                 'tp2'})}])

        self.assert_(len(res) == 4)
        self.assert_(filter(lambda x: x.name == 'tp2', res) == [])

    def testQuery(self):
        
        # things
        t1 = Thing('tp')
        t2 = Thing('t2')
        t3 = Thing('t3')
        t4 = Thing('t4')
        t5 = Thing('t5')

        t2.addAttr('attr1', '1')
        t2.addAttr('attr2', '2')

        t4.addAttr('attr1', '1')
        t4.addAttr('attr2', '2')
        
        # part
        tp1 = Part('tp1')
        tp2 = Part('tp2')
        tp3 = Part('tp3')

        t1.connect(t2)
        t1.connect(tp1)
        tp1.connect(t3)
        tp1.connect(tp2)
        tp2.connect(t4)
        
        clusto.flush()
    

