import clusto
from clusto.test import testbase 
import itertools

from clusto.drivers import *

from clusto.drivers.resourcemanagers.simplenamemanager import SimpleNameManagerException


class ResourceManagerTests(testbase.ClustoTestBase):

    def testAllocate(self):

        rm = ResourceManager('test')
        d = Driver('d')

        rm.allocate(d, 'foo')

        self.assertEqual(rm.owners('foo'), [d])

    def testResourceCount(self):

        rm = ResourceManager('test')
        d = Driver('d')
        
        rm.allocate(d, 'foo')
        rm.allocate(d, 'bar')
        
        self.assertEqual(rm.count, 2)

    def testDeallocate(self):

        rm = ResourceManager('test')
        d = Driver('d')

        rm.allocate(d, 'foo')
        self.assertEqual(rm.count, 1)

        rm.deallocate(d, 'foo')
        self.assertEqual(rm.count, 0)
        self.assertEqual(rm.owners('foo'), [])

    def testGeneralDeallocate(self):

        rm = ResourceManager('test')
        d = Driver('d')

        rm.allocate(d, 'foo')
        rm.allocate(d, 'bar')
        
        self.assertEqual(rm.count, 2)
        self.assertEqual(sorted([x.subkey for x in rm.resources(d)]),
                         sorted(['foo', 'bar']))

        rm.deallocate(d)

        self.assertEqual(rm.count, 0)
        self.assertEqual(sorted(rm.resources(d)),
                         sorted([]))

