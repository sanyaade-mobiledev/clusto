"""
Test the basic Driver object
"""

import unittest
import testbase
import datetime

import clusto

from clusto.drivers.Base import *


class TestDriverAttributes(testbase.ClustoTestBase):

    def testGettingAttrs(self):

        d1 = Driver('d1')

        d1.addAttr('foo', 'bar')
        d1.addAttr('foo0', 'bar1')

        self.assertEqual(sorted((i.key for i in d1.attrs())),
                         ['foo', 'foo0'])

        alist = d1.attrs(numbered=True)

        self.assertEqual(sorted(i.key for i in alist),
                         sorted(['foo0']))

    def testGettingAttrsMultipleTimes(self):
        d1 = Driver('d1')
        d2 = Driver('d2')
        
        d1.addAttr('foo', 'bar')
        d1.addAttr('foo0', 'bar1')
        d2.addAttr('d1', d1)

        clusto.flush()

        d = clusto.getByName('d1')
        
        self.assertEqual(len(d.references()), 1)
        self.assertEqual(len(d.attrs()), 2)


        
        
    def testNumberedAttrs(self):

        d1 = Driver('d1')

        d1.addAttr('foo', 'bar')

        d1.addAttr('foo', 'bar1', numbered=5)
        d1.addAttr('foo', 'bar2', numbered=6)

        clusto.flush()

        self.assertEqual(sorted(d1.attrKeys()),
                         sorted(['foo', 'foo5', 'foo6']))

        self.assertEqual(sorted(d1.attrKeys(numbered=True)),
                         sorted(['foo5', 'foo6']))

    def testAutoNumberedAttrs(self):
        d1 = Driver('d1')

        d1.addAttr('foo', 'bar')

        d1.addAttr('foo', 'bar1', numbered=True)
        d1.addAttr('foo', 'bar2', numbered=True)

        clusto.flush()

        self.assertEqual(sorted(d1.attrKeys()),
                         sorted(['foo', 'foo0', 'foo1']))

        self.assertEqual(sorted(d1.attrKeys(numbered=True)),
                         sorted(['foo0', 'foo1']))
        
    def testSubKeyAttrs(self):

        d1 = Driver('d1')

        d1.addAttr('foo', 'bar', subkey='subfoo')
        d1.addAttr('foo', 'caz', subkey='subbar')

        self.assertEqual(sorted(d1.attrKeys()),
                         sorted(['foo-subfoo', 'foo-subbar']))

    def testNumberedAttrsWithSubKeys(self):

        d1 = Driver('d1')

        d1.addAttr(key='foo', value='bar1', numbered=True, subkey='one')
        d1.addAttr(key='foo', value='bar2', numbered=True, subkey='two')

        self.assertEqual(sorted(d1.attrItems()),
                         sorted([('foo0-one', 'bar1'),
                                 ('foo1-two', 'bar2')]))

    def testGettingSpecificNumberedAttrs(self):
        
        d1 = Driver('d1')

        d1.addAttr(key='foo', value='bar1', numbered=True, subkey='one')
        d1.addAttr(key='foo', value='bar2', numbered=True, subkey='two')
        d1.addAttr(key='foo', value='bar3', numbered=True, subkey='three')
        d1.addAttr(key='foo', value='bar4', numbered=True, subkey='four')

        self.assertEqual(list(d1.attrItems(key='foo', numbered=2)),
                         [('foo2-three', 'bar3')])
        
        self.assertEqual(list(d1.attrItems(key='foo', numbered=0)),
                         [('foo0-one', 'bar1')])
        
    def testGettingAttrsWithSpecificValues(self):

        d1 = Driver('d1')

        d1.addAttr(key='foo', value='bar1', numbered=True, subkey='one')
        d1.addAttr(key='foo', value='bar2', numbered=True, subkey='two')
        d1.addAttr(key='foo', value='bar3', numbered=True, subkey='three')
        d1.addAttr(key='foo', value='bar4', numbered=True, subkey='four')

        self.assertEqual(list(d1.attrItems(value='bar3')),
                         [('foo2-three', 'bar3')])
        
        self.assertEqual(list(d1.attrItems(value='bar1')),
                         [('foo0-one', 'bar1')])
        

                          
    def testDelAttrs(self):
        d1 = Driver('d1')

        d1.addAttr(key='foo', value='bar1', numbered=True, subkey='one')
        d1.addAttr(key='foo', value='bar2', numbered=True, subkey='two')
        d1.addAttr(key='foo', value='bar3', numbered=True, subkey='three')
        d1.addAttr(key='foo', value='bar4', numbered=True, subkey='four')

        d1.delAttrs(key='foo', value='bar4')

        
        self.assertEqual(list(d1.attrItems(value='bar4')),
                         [])

        self.assertEqual(list(d1.attrItems(value='bar3')),
                         [('foo2-three', 'bar3')])

        d1.delAttrs(key='foo', subkey='three', numbered=2)
        self.assertEqual(list(d1.attrItems(value='bar3')),
                         [])


    def testHasAttr(self):
        
        d1 = Driver('d1')

        d1.addAttr(key='foo', value='bar1', numbered=True, subkey='one')
        d1.addAttr(key='foo', value='bar2', numbered=True, subkey='two')
        d1.addAttr(key='foo', value='bar3', numbered=True, subkey='three')
        d1.addAttr(key='foo', value='bar4', numbered=True, subkey='four')

        self.assertFalse(d1.hasAttr(key='foo'))
        self.assertTrue(d1.hasAttr(key='foo', numbered=True, strict=False))
        self.assertTrue(d1.hasAttr(key='foo1', subkey='two'))

    def testHiddenAttrs(self):

        d1 = Driver('d1')

        d1.addAttr(key='foo', value='bar1', numbered=True, subkey='one')
        d1.addAttr(key='foo', value='bar2', numbered=True, subkey='two')
        d1.addAttr(key='_foo', value='bar3', numbered=True, subkey='three')
        d1.addAttr(key='_foo', value='bar4', numbered=True, subkey='four')

        self.assertEqual(sorted(d1.attrItems(ignoreHidden=True)),
                         sorted([('foo0-one', 'bar1'), ('foo1-two', 'bar2')]))


    def testAttributeGetValueAfterAdd(self):

        d1 = Driver('d1')

        d1.addAttr('foo', 2)
        self.assertEqual(sorted(d1.attrItems('foo')), [('foo', 2)])
        d1.addAttr('bar', 3)
        self.assertEqual(sorted(d1.attrItems('foo')), [('foo', 2)])
        self.assertEqual(sorted(d1.attrItems('bar')), [('bar', 3)])



        
