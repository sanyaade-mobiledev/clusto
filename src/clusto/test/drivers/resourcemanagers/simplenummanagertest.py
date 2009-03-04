import clusto
from clusto.test import testbase 
import itertools

from clusto.drivers import *

from clusto.drivers.resources.simplenummanager import *



class SimpleNumManagerTests(testbase.ClustoTestBase):

    def data(self):

        n1 = SimpleNumManager('numgen1', startingnum=1)


        n2 = SimpleNumManager('numgen2', maxnum=4, startingnum=0)
        
        clusto.flush()

    def testAllocateNum(self):

        ngen = clusto.getByName('numgen1')
        
        d = Driver('foo')
        s1 = ngen.allocate(d)
        s2 = ngen.allocate(d)
        s3 = ngen.allocate(d)
        s4 = ngen.allocate(d)

        self.assertEqual(ngen.owners('num', 1), [d])
        self.assertEqual(ngen.owners('num', 2), [d])
        self.assertEqual(ngen.owners('num', 3), [d])
        self.assertEqual(ngen.owners('num', 4), [d])


    def testAllocateMaxNum(self):
        
        d = Driver('foo')

        ngen = clusto.getByName('numgen2')

        s1 = ngen.allocate(d)
        s1 = ngen.allocate(d)
        s1 = ngen.allocate(d)
        s1 = ngen.allocate(d)
        s1 = ngen.allocate(d)

        self.assertRaises(SimpleNumManagerException, ngen.allocate, d)
        
        
