"""
Test the basic Driver object
"""

import unittest
from clusto.test import testbase
import datetime

import clusto
from clusto import Attribute
from clusto.drivers.base import *
from clusto.exceptions import *

class TestDriverAttributes(testbase.ClustoTestBase):

    def testSetAttrs(self):

        d1 = Driver('d1')
        d1.set_attr('foo', 'bar')

        self.assertEqual(d1.attrItems(),
                         [(('foo', None, None), 'bar')])

        d1.set_attr('foo', 'bar2')
        self.assertEqual(d1.attrItems(),
                         [(('foo', None, None), 'bar2')])

        d1.addAttr('foo', 'bar3')

        self.assertEqual(sorted(d1.attrItems()),
                         sorted(
                         [(('foo', None, None), 'bar2'),
                          (('foo', None, None), 'bar3')]))

        self.assertRaises(DriverException, d1.set_attr, 'foo', 'bar4')


        d2 = Driver('d2')
        d2.addAttr('a', number=0, subkey='foo', value='bar1')
        d2.addAttr('a', number=1, subkey='foo', value='bar1')
        d2.addAttr('a', number=2, subkey='foo', value='bar1')

        d2.set_attr('a', 't1')

        self.assertEqual(sorted(d2.attrItems()),
                         sorted([(('a', 0, 'foo'), 'bar1'),
                                 (('a', 1, 'foo'), 'bar1'),
                                 (('a', 2, 'foo'), 'bar1'),
                                 (('a', None, None), 't1'),]))

    def testGettingAttrs(self):

        d1 = Driver('d1')

        d1.addAttr('foo', 'bar')
        d1.addAttr('foo', 'bar1', number=0)

        self.assertEqual(sorted(d1.attrItems()),
                         [(('foo', None, None), 'bar'), 
                          (('foo', 0, None), 'bar1')])



        self.assertEqual(d1.attrItems(number=True),
                         [(('foo', 0, None), 'bar1')])

    def testGettingAttrValues(self):
        d1 = Driver('d1')
        d2 = Driver('d2')
        
        d1.addAttr('foo', 'bar')
        d1.addAttr('foo0', 'bar1')
        d2.addAttr('d1', d1)

        clusto.flush()

        self.assertEqual(sorted(['bar', 'bar1']),
                         sorted(d1.attrValues('foo.*', regex=True)))

        self.assertEqual([d1], d2.attrValues())
        

    def testGettingAttrsMultipleTimes(self):
        d1 = Driver('d1')
        d2 = Driver('d2')
        
        d1.addAttr('foo', 'bar')
        d1.addAttr('foo0', 'bar1')
        d2.addAttr('d1', d1)

        clusto.flush()

        d = clusto.get_by_name('d1')
        
        self.assertEqual(len(d.references()), 1)
        self.assertEqual(len(d.attrs()), 2)


        
        
    def testNumberedAttrs(self):

        d1 = Driver('d1')

        d1.addAttr('foo', 'bar')

        d1.addAttr('foo', 'bar1', number=5)
        d1.addAttr('foo', 'bar2', number=6)

        clusto.flush()

        self.assertEqual(sorted(d1.attrItems()),
                         sorted([(('foo', None, None), 'bar'), 
                          (('foo', 5, None), 'bar1'), 
                          (('foo', 6, None), 'bar2')]))

        self.assertEqual(sorted(d1.attrItems(number=True)),
                         sorted([(('foo', 5, None), 'bar1'), 
                          (('foo', 6, None), 'bar2')]))


    def testAutoNumberedAttrs(self):
        d1 = Driver('d1')

        d1.addAttr('foo', 'bar')

        d1.addAttr('foo', 'bar1', number=True)
        d1.addAttr('foo', 'bar2', number=True)

        clusto.flush()

        self.assertEqual(sorted(d1.attrItems()),
                         sorted([(('foo', None, None), 'bar'),
                                 (('foo', 0, None), 'bar1'),
                                 (('foo', 1, None), 'bar2')]))

        self.assertEqual(sorted(d1.attrItems(number=True)),
                         sorted([(('foo', 0, None), 'bar1'),
                                 (('foo', 1, None), 'bar2')]))

        
    def testSubKeyAttrs(self):

        d1 = Driver('d1')

        d1.addAttr('foo', 'bar', subkey='subfoo')
        d1.addAttr('foo', 'caz', subkey='subbar')

        self.assertEqual(sorted(d1.attrKeyTuples()),
                         sorted([('foo',None,'subfoo'), ('foo',None,'subbar')]))

    def testNumberedAttrsWithSubKeys(self):

        d1 = Driver('d1')

        d1.addAttr(key='foo', value='bar1', number=True, subkey='one')
        d1.addAttr(key='foo', value='bar2', number=True, subkey='two')
        
        self.assertEqual(d1.attrItems(),
                         [(('foo', 0, 'one'), 'bar1'),
                          (('foo', 1, 'two'), 'bar2')])

    def testGettingSpecificNumberedAttrs(self):
        
        d1 = Driver('d1')

        d1.addAttr(key='foo', value='bar1', number=True, subkey='one')
        d1.addAttr(key='foo', value='bar2', number=True, subkey='two')
        d1.addAttr(key='foo', value='bar3', number=True, subkey='three')
        d1.addAttr(key='foo', value='bar4', number=True, subkey='four')

        self.assertEqual(list(d1.attrItems(key='foo', number=2)),
                         [(('foo',2,'three'), 'bar3')])
        
        self.assertEqual(list(d1.attrItems(key='foo', number=0)),
                         [(('foo',0,'one'), 'bar1')])
        
    def testGettingAttrsWithSpecificValues(self):

        d1 = Driver('d1')

        d1.addAttr(key='foo', value='bar1', number=True, subkey='one')
        d1.addAttr(key='foo', value='bar2', number=True, subkey='two')
        d1.addAttr(key='foo', value='bar3', number=True, subkey='three')
        d1.addAttr(key='foo', value='bar4', number=True, subkey='four')

        self.assertEqual(list(d1.attrItems(value='bar3')),
                         [(('foo',2,'three'), 'bar3')])
        
        self.assertEqual(list(d1.attrItems(value='bar1')),
                         [(('foo',0,'one'), 'bar1')])
        

                          
    def testDelAttrs(self):
        d1 = Driver('d1')

        d1.addAttr(key='foo', value='bar1', number=True, subkey='one')
        d1.addAttr(key='foo', value='bar2', number=True, subkey='two')
        d1.addAttr(key='foo', value='bar3', number=True, subkey='three')
        d1.addAttr(key='foo', value='bar4', number=True, subkey='four')

        d1.delAttrs(key='foo', value='bar4')

        
        self.assertEqual(list(d1.attrItems(value='bar4')),
                         [])

        self.assertEqual(list(d1.attrItems(value='bar3')),
                         [(('foo',2,'three'), 'bar3')])

        d1.delAttrs(key='foo', subkey='three', number=2)
        self.assertEqual(list(d1.attrItems(value='bar3')),
                         [])


    def testHasAttr(self):
        
        d1 = Driver('d1')

        d1.addAttr(key='foo', value='bar1', number=True, subkey='one')
        d1.addAttr(key='foo', value='bar2', number=True, subkey='two')
        d1.addAttr(key='foo', value='bar3', number=True, subkey='three')
        d1.addAttr(key='foo', value='bar4', number=True, subkey='four')

        self.assertFalse(d1.has_attr(key='foo', number=False))
        self.assertTrue(d1.has_attr(key='foo', number=True))
        self.assertTrue(d1.has_attr(key='foo', number=1, subkey='two'))

    def testHiddenAttrs(self):

        d1 = Driver('d1')

        d1.addAttr(key='foo', value='bar1', number=True, subkey='one')
        d1.addAttr(key='foo', value='bar2', number=True, subkey='two')
        d1.addAttr(key='_foo', value='bar3', number=True, subkey='three')
        d1.addAttr(key='_foo', value='bar4', number=True, subkey='four')

        self.assertEqual(d1.attrItems(ignore_hidden=True),
                         [(('foo',0,'one'), 'bar1'), (('foo',1,'two'), 'bar2')])


    def testAttributeGetValueAfterAdd(self):

        d1 = Driver('d1')

        d1.addAttr('foo', 2)
        self.assertEqual(d1.attrItems('foo'), [(('foo',None,None), 2)])
        d1.addAttr('bar', 3)
        self.assertEqual(d1.attrItems('foo'), [(('foo',None,None), 2)])
        self.assertEqual(d1.attrItems('bar'), [(('bar',None,None), 3)])


    def testGetByAttr(self):

        d1 = Driver('d1')
        d1.addAttr('foo', 1)

        d2 = Driver('d2')
        d2.addAttr('foo', 2)

        d3 = Driver('d3')
        d3.addAttr('bar', 3)

        clusto.flush()

        result = Driver.getByAttr('foo', 2)

        self.assertEqual(result, [d2])
        
    def testAttrCount(self):
        
        d1 = Driver('d1')

        d1.addAttr(key='foo', value='bar1', number=True, subkey='one')
        d1.addAttr(key='foo', value='bar2', number=True, subkey='two')
        d1.addAttr(key='foo', value='bar3', number=True, subkey='three')
        d1.addAttr(key='foo', value='bar4', number=True, subkey='four')
        
        self.assertEqual(d1.attr_query(key='foo', number=2, count=True), 1)
        
        self.assertEqual(d1.attr_query(key='foo', number=0, count=True), 1)

        self.assertEqual(d1.attr_query(key='foo', number=False, count=True), 0)
        self.assertEqual(d1.attr_query(key='foo', count=True), 4)

        self.assertEqual(d1.attr_query(subkey='four', count=True), 1)


        d1.delAttrs(key='foo', value='bar1', number=True, subkey='one')
        d1.addAttr(key='foo', value='bar5', number=True, subkey='five')
        self.assertEqual(d1.attr_query(key='foo', number=0, count=True), 0)
        self.assertEqual(d1.attr_query(key='foo', number=4, count=True), 1)
        
        
    def testAddAttributeDirectly(self):

        d1 = Driver('d1')
        d2 = Driver('d2')


        
        d1.addAttr(Attribute(key='foo',                             
                             value='bar'))

        d2.addAttr(Attribute(key='foo1',
                             value=d1.entity))

        self.assertEqual(len(d1.attrs(key='foo')), 1)
        self.assertEqual(len(d2.attrs(key='foo1')), 1)
        

class TestDriverContainerFunctions(testbase.ClustoTestBase):
    
    def testInsert(self):

        d1 = Driver('d1')
        d2 = Driver('d2')

        d1.insert(d2)
        
        clusto.flush()

        d = clusto.get_by_name('d1')

        self.assertEqual(d.attrItems(ignore_hidden=False),
                         [(('_contains', 0, None), d2)])

    def testRemove(self):
        
        d1 = Driver('d1')
        d2 = Driver('d2')

        d1.insert(d2)
        
        clusto.flush()

        d = clusto.get_by_name('d1')
        d.remove(d2)

        clusto.flush()

        self.assertEqual(d.attrItems(ignore_hidden=False),
                         [])

    def testContents(self):
        
        d1 = Driver('d1')
        d2 = Driver('d2')

        d1.insert(d2)
        
        self.assertEqual(d1.contents(), [d2])
                         

    def testMultipleInserts(self):

        d1 = Driver('d1')
        d2 = Driver('d2')
        d3 = Driver('d3')

        d1.insert(d2)
        
        self.assertRaises(TypeError, d3.insert, d2)

    def testNumberedInserts(self):

        d1 = Driver('d1')

        d1.insert(Driver('d2'))
        d1.insert(Driver('d3'))
        d1.insert(Driver('d4'))
        d1.insert(Driver('d5'))
        d1.insert(Driver('d6'))

        
        self.assertEqual(range(5),
                         [x.number for x in d1.attrs(ignore_hidden=False)])
        


class TestDriver(testbase.ClustoTestBase):
    
    def testCreatingDriverWithUsedName(self):
        
        d1 = Driver('d1')

        self.assertRaises(NameException, Driver, 'd1')

        d1.attrs()

    def testDriverSets(self):
        
        d1 = Driver('d1')
        d2 = Driver('d2')

        s = set([d1,d1,d2])

        self.assertEquals(len(s), 2)

class TestDriver(Driver):

    _clusto_type = "tester"
    _driver_name = "testdriver"

    _properties = {'propA': None,
                   'propB': 'foo',
                   'propC': 5 }

class TestDriverProperties(testbase.ClustoTestBase):
    
    def testPropDefaultGetter(self):

        d = TestDriver('d')

        self.assertEqual(None, d.propA)
        self.assertEqual('foo', d.propB)
        self.assertEqual(5, d.propC)

    def testPropSetter(self):

        d = TestDriver('d')

        self.assertEqual(None, d.propA)

        d.propA = 'foo'
        self.assertEqual('foo', d.propA)

        d.propA = 'bar'
        self.assertEqual('bar', d.propA)

        d.propA = 10
        self.assertEqual(10, d.propA)

    def testPropSetterMultipleObjects(self):
        d = TestDriver('d')
        d2 = TestDriver('d2')

        d.propB = 'bar'
        d2.propB = 'cat'

        self.assertEqual(d2.propB, 'cat')
        self.assertEqual(d.propB, 'bar')

class TestDriverQueries(testbase.ClustoTestBase):
    
    def data(self):

        d1 = Driver('d1')
        d2 = Driver('d2')
        d3 = Driver('d3')

        d1.addAttr('_foo', 'bar1')
        d1.addAttr('car', 'baz')
        d1.addAttr('car', 'baz')
        d1.addAttr('d', 'dee', number=True)
        d1.addAttr('d', 'dee', number=True)
        d1.addAttr('a', 1)
        d1.addAttr('a', 1, subkey='t')
        d1.addAttr('a', 1, subkey='g')
        d1.addAttr('a', 1, subkey='z', number=4)
        d1.addAttr('a', 1, subkey='z', number=5)
        d1.addAttr('a', 1, subkey='z', number=6)
        
        d1.set_attr('d2', d2)
        d1.set_attr('d3', d3)

        d2.set_attr('aaa', 1)
        d2.set_attr('aab', 2)
        d2.set_attr('aac', 3)



    def testAttrAndQueryEqual(self):

        d1 = clusto.get_by_name('d1')
        d2 = clusto.get_by_name('d2')
        d3 = clusto.get_by_name('d3')

        self.assertEqual(d1.attrs('a'), d1.attr_query('a'))

        self.assertEqual(d1.attrs('a', 1), d1.attr_query('a', 1))

        self.assertEqual(d1.attrs('a', 1, number=True), 
                         d1.attr_query('a', 1, number=True))

        self.assertEqual(d1.attrs('a', 1, number=5), 
                         d1.attr_query('a', 1, number=5))

        self.assertEqual(d1.attrs(value='dee'), 
                         d1.attr_query(value='dee'))


        self.assertEqual(d1.attrs(value='_foo'), 
                         d1.attr_query(value='_foo'))

        self.assertEqual(d1.attrs(key='_foo'), 
                         d1.attr_query(key='_foo'))

        self.assertEqual(d1.attrs(key='a', subkey=None), 
                         d1.attr_query(key='a', subkey=None))

        self.assertEqual(d1.attrs(value=d2), 
                         d1.attr_query(value=d2))


        self.assertEqual(d1.attrs(subkey='z'),
                         d1.attr_query(subkey='z'))


    def testDoAttrQuery(self):

        d1 = clusto.get_by_name('d1')
        d2 = clusto.get_by_name('d2')
        self.assertEqual(set(Driver.getByAttr(key='a*')),
                         set([d1,d2]))
