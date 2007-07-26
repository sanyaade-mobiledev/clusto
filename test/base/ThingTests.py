import unittest
#from clusto.schema import *
import clusto
from clusto.drivers.Base import *

class TestThingSchema(unittest.TestCase):

    def setUp(self):
        
        metadata.connect('sqlite:///:memory:')
        metadata.create_all()



    def tearDown(self):

        ctx.current.clear()
        metadata.dispose()

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

        
