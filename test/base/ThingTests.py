import unittest
from clusto.schema import METADATA, CTX
import clusto
from clusto.drivers.Base import *

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

        tq = Thing.selectone(Thing.c.name == 'foo1')

        self.assertEqual(Thing.meta_attrs['clustotype'],
                         tq.getAttr('clustotype'))

        
        self.assertEqual('one',
                         tq.getAttr('attr1'))

    def testMulitpleValuesForSameAttrKeyTest(self):

        t1 = Thing('foo1')

        t1.addAttr('attr1', 1)
        t1.addAttr('attr1', 2)
        t1.addAttr('attr1', 3)

        clusto.flush()

        tq = Thing.selectone(Thing.c.name == 'foo1')

        values = tq.getAttr('attr1', justone=False)

        self.assertEqual(3, len(values))

        values.sort()

        self.assertEqual([1,2,3], values)

    def testAttrOperations(self):

        t1 = Thing('foo1')

        clusto.flush()

        t1.setAttrs('attr1', [1,2,3,4,5])

        clusto.flush()

        tq = Thing.selectone(Thing.c.name == 'foo1')
        
        values = tq.getAttr('attr1', justone=False)
        
        self.assertEqual(5, len(values))

        tq.delAttr('attr1', 2)

        clusto.flush()

        v = tq.getAttr('attr1', justone=False)
        v.sort()
        
        self.assertEqual([1,3,4,5], v)
        
        tq.setAttrs('attr1', ['a','b'])

        clusto.flush()
        tq = Thing.selectone(Thing.c.name == 'foo1')

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

        tt2 = Thing.selectone(Thing.c.name == 'foo2')
        tt3 = Thing.selectone(Thing.c.name == 'foo3')

        tt3.connect(tt2)
        clusto.flush()

        self.assert_(tt2 in tt3.connections)
        self.assert_(t1 in tt3.connections)

        tt2.disconnect(tt3)
        clusto.flush()
        
        self.assert_(tt2 not in tt3.connections)
        
    def testIsPart(self):

        t1 = Thing('foo1')

        self.assertEqual(t1.isPart(), False)

        t2 = Part('part1')

        self.assertEqual(t2.isPart(), True)

        clusto.flush()

        tq1 = Thing.selectone(Thing.c.name == 'part1')

        self.assert_(tq1.isPart())
        
        
