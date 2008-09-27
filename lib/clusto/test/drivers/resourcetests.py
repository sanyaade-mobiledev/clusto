import clusto
from clusto.test import testbase 
import itertools

from clusto.drivers import *

from clusto.drivers.resources.simplenamemanager import SimpleNameManagerException


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

class SimpleNameResourceTests(testbase.ClustoTestBase):

    def data(self):

        n1 = SimpleNameManager('foonamegen',
                               basename='foo',
                               digits=4,
                               startingnum=1,
                               )


        n2 = SimpleNameManager('barnamegen',
                               basename='bar',
                               digits=2,
                               startingnum=95,
                               )
        
        clusto.flush()

    def testNamedDriverCreation(self):
        ngen = clusto.getByName('foonamegen')
        
        s1 = ngen.createEntity(Driver)

        clusto.flush()

        d1 = clusto.getByName('foo0001')

        self.assertEquals(s1.name, d1.name)
        
    def testAllocateName(self):

        ngen = clusto.getByName('foonamegen')
        
        s1 = ngen.createEntity(Driver)
        s2 = ngen.createEntity(Driver)
        s3 = ngen.createEntity(Driver)
        s4 = ngen.createEntity(Driver)

        clusto.flush()

        self.assertEqual(s1.name, 'foo0001')
        self.assertEqual(s2.name, 'foo0002')
        self.assertEqual(s3.name, 'foo0003')
        self.assertEqual(s4.name, 'foo0004')
        
    def testNoLeadingZeros(self):

        ngen = clusto.getByName('barnamegen')

        s1 = ngen.createEntity(Driver)
        s2 = ngen.createEntity(Driver)
        s3 = ngen.createEntity(Driver)
        s4 = ngen.createEntity(Driver)

        clusto.flush()

        self.assertEqual(s1.name, 'bar95')
        self.assertEqual(s2.name, 'bar96')
        self.assertEqual(s3.name, 'bar97')
        self.assertEqual(s4.name, 'bar98')

    def testTooManyDigits(self):
        
        ngen = clusto.getByName('barnamegen')

        s1 = ngen.createEntity(Driver)
        s2 = ngen.createEntity(Driver)
        s3 = ngen.createEntity(Driver)
        s4 = ngen.createEntity(Driver)

        s5 = ngen.createEntity(Driver)
        self.assertRaises(SimpleNameManagerException,
                          ngen.createEntity, Driver)

