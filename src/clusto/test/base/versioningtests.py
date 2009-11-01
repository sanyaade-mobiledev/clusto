import unittest
from clusto.test import testbase

import clusto
from clusto.schema import *
from clusto.drivers.base import *
from clusto.drivers import BasicDatacenter
from sqlalchemy.exceptions import InvalidRequestError

class TestClustoVersioning(testbase.ClustoTestBase):

    def testGetFirstVersionNumber(self):

        curver = clusto.get_latest_version_number()
        self.assertEqual(curver, 2)

    def testVersionIncrementing(self):

        curver = clusto.get_latest_version_number()

        e1 = Entity('e1')
        e2 = Entity('e2')

        self.assertEqual(clusto.get_latest_version_number(), curver + 2)

    def testVersionIncrementWithAttrs(self):

        curver = clusto.get_latest_version_number()
        
        e1 = Entity('e1')
        e2 = Entity('e2')

        e1.add_attr('foo', 2)

        
        self.assertEqual(clusto.get_latest_version_number(), curver + 3)
        
        
    def testDeleteVersion(self):

        curver = clusto.get_latest_version_number()

        e1 = Entity('e1')
        etest = clusto.get_by_name('e1')
        e1.delete()


        self.assertRaises(LookupError, clusto.get_by_name, 'e1')

        e1a = Entity('e1')

        etest = clusto.get_by_name('e1')

        self.assertEqual(etest.entity.version, curver+3)


    def testViewOldVersion(self):

        curver = clusto.get_latest_version_number()

        e1 = Entity('e1')
        e2 = Entity('e2')
        e3 = Entity('e3')

        self.assertEqual(Entity.query().filter(Entity.name.like('e%')).count(),
                         3)

        SESSION.version = curver

        self.assertEqual(Entity.query().filter(Entity.name.like('e%')).count(),
                         0)

        SESSION.version = clusto.working_version()

        self.assertEqual(Entity.query().filter(Entity.name.like('e%')).count(),
                         3)

        SESSION.version = curver + 1

        self.assertEqual(Entity.query().filter(Entity.name.like('e%')).count(),
                         1)


        SESSION.version = curver + 2

        self.assertEqual(sorted([e1,e2]),
                         Entity.query().filter(Entity.name.like('e%')).all())

    def testOldVersionsOfAttributes(self):

        curver = clusto.get_latest_version_number()

        e1 = Entity('e1')
        e2 = Entity('e2')

        e1.add_attr('foo', 1)
        e1.add_attr('foo2', 2)
        e1.add_attr('foo3', 3)

        SESSION.version = curver + 3

        self.assertEqual(len(list(e1.attrs)), 1)
        
        e = Entity.query().filter_by(name='e1').one()

        SESSION.version = curver + 4

        self.assertEqual(sorted([a.key for a in e.attrs]),
                         sorted(['foo', 'foo2']))


    def testAttributesImmutable(self):

        e1 = Entity('e1')
        e1.add_attr('foo', 1)

        a = e1.attrs[0]

        self.assertRaises(Exception, setattr, a.value, 2)

        
