import clusto
from clusto.test import testbase 
import itertools

from clusto.drivers import *
from clusto.exceptions import ResourceLockException
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


class ResourceLockTests(testbase.ClustoTestBase):

    def data(self):

        rm = ResourceManager('test')

        d = Driver('d')
        e = Driver('e')
        
        
    def testDeallocatingLockedResource(self):

        d, e = clusto.getEntities(clustodrivers=[Driver])

        rm = clusto.getEntities(clustodrivers=[ResourceManager])[0]
        
        rm.allocate(d, 'foo')
        rm.allocate(d, 'bar')

        rm.lockResource(d, 'foo')
        
        self.assertRaises(ResourceLockException, rm.deallocate, d, 'foo')


    
    def testLockingAnAlreadyLockedResource(self):

        d, e = clusto.getEntities(clustodrivers=[Driver])

        rm = clusto.getEntities(clustodrivers=[ResourceManager])[0]
        
        rm.allocate(d, 'foo')
        rm.allocate(d, 'bar')

        rm.lockResource(d, 'foo')

        self.assertRaises(ResourceLockException, rm.lockResource, d, 'foo')

        

    def testDeallocatingAllResourcesFromAnEntity(self):

        d, e = clusto.getEntities(clustodrivers=[Driver])

        rm = clusto.getEntities(clustodrivers=[ResourceManager])[0]
        
        rm.allocate(d, 'foo')
        rm.allocate(d, 'bar')

        rm.lockResource(d, 'foo')

        rm.unlockResource(d, 'foo')

        rm.deallocate(d, 'foo')
        
        
        
        
