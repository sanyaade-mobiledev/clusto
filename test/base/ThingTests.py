import unittest
from clusto.schema import METADATA, CTX, AttributeDict
import clusto
from clusto.drivers.Base import Thing, Part
from clusto.drivers.Servers import Server

class TestThingSchema(unittest.TestCase):

    def setUp(self):
        
        METADATA.connect('sqlite:///:memory:')
        METADATA.create_all()



    def tearDown(self):

        CTX.current.clear()
        METADATA.dispose()


    def testThingObject(self):

        t1 = Thing('foo1')
        t2 = Thing('foo2')
        
        clusto.flush()

        ts = Thing.select()

        self.assertEqual(2, len(ts))

    def testThingWithSameName(self):
        """
        I shouldn't be able to have to Things with the same name
        """
        
        t1 = Thing('foo1')
        t2 = Thing('foo1')

        # maybe test for a more specific exception in the future
        self.assertRaises(Exception, clusto.flush)

    def testAddingAttributeToThing(self):

        t1 = Thing('foo1')

        t1.addAttr('attr1', 'one')

        clusto.flush()

        tq = clusto.getByName('foo1')

        
        self.assertEqual('one',
                         tq.getAttr('attr1'))

    def testMulitpleValuesForSameAttrKeyTest(self):

        t1 = Thing('foo1')

        t1.addAttr('attr1', 1)
        t1.addAttr('attr1', 2)
        t1.addAttr('attr1', 3)

        clusto.flush()

        tq = clusto.getByName('foo1')

        values = tq.getAttr('attr1', justone=False)

        self.assertEqual(3, len(values))

        values.sort()

        self.assertEqual([1,2,3], values)

    def testAttrOperations(self):

        t1 = Thing('foo1')

        clusto.flush()

        t1.setAttrs('attr1', [1,2,3,4,5])

        clusto.flush()

        tq = clusto.getByName('foo1')
        
        values = tq.getAttr('attr1', justone=False)
        
        self.assertEqual(5, len(values))

        tq.delAttr('attr1', 2)

        clusto.flush()

        v = tq.getAttrs(['attr1'], onlyvalues=True)#, justone=False)
        v.sort()
        
        self.assertEqual([1,3,4,5], v)
        
        tq.setAttrs('attr1', ['a','b'])

        clusto.flush()
        tq = clusto.getByName('foo1')

        values = tq.getAttr('attr1', justone=False)

        self.assertEqual(2, len(values))

        

    def testConnectingThings(self):

        t1 = Thing('foo1')
        t2 = Thing('foo2')
        t3 = Thing('foo3')
        
        clusto.flush()

        t1.connect(t2)
        t1.connect(t3)

        clusto.flush()
        
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
        

    def testIsMatch(self):

        t1 = Thing('t1')
        t2 = Thing('t2')

        t1.addAttr('a1', 1)
        t1.addAttr('a1', 3)
        t1.addAttr('a2', 2)
        clusto.flush()

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

        
        



    def testGetAttrs(self):

        t1 = Thing('t1')
        t1.addAttr('a', 1)
        t1.addAttr('a', 2)
        t1.addAttr('b', 3)
        
        clusto.flush()

        t = clusto.getByName('t1')

        self.assert_(t.getAttrs(onlyvalues=True, sort=True) == [1, 2, 3])

    def testConnectionSearchForType(self):

        # Servers
        t1 = Server('t1')
        t2 = Server('t2')
        t3 = Server('t3')
        t4 = Server('t4')
        t5 = Server('t5')

        t2.addAttr('attr1', 1)
        t2.addAttr('attr2', 2)

        t4.addAttr('attr1', 1)
        t4.addAttr('attr2', 2)
        
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

        t1 = clusto.getByName('t1')

        result2 = t1.searchConnections([{'matchdict': AttributeDict(Server.allMetaAttrs())}])

        result2.sort(cmp=lambda x, y: cmp(x.name, y.name))

        expectedresult = [t2, t4, t3]
        expectedresult.sort(cmp=lambda x, y: cmp(x.name, y.name))

        
        self.assert_(result2 == expectedresult)
        

    def testConnectionsSearch(self):

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

        tp = clusto.getByName('tp')

        
        query = [{'matchdict': AttributeDict({'attr1':'1',
                                              'attr2':'2'})}]
        
        result = tp.searchConnections(query)

        result.sort(cmp=lambda x, y: cmp(x.name, y.name))

        expectedresult = [t2, t4]
        expectedresult.sort(cmp=lambda x, y: cmp(x.name, y.name))
        
            
        self.assert_(result == expectedresult)

        
