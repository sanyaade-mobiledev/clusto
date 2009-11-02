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

        SESSION.clusto_version = curver

        self.assertEqual(Entity.query().filter(Entity.name.like('e%')).count(),
                         0)

        SESSION.clusto_version = clusto.working_version()

        self.assertEqual(Entity.query().filter(Entity.name.like('e%')).count(),
                         3)

        SESSION.clusto_version = curver + 1

        self.assertEqual(Entity.query().filter(Entity.name.like('e%')).count(),
                         1)


        SESSION.clusto_version = curver + 2

        self.assertEqual(sorted([e1,e2]),
                         Entity.query().filter(Entity.name.like('e%')).all())

    def testOldVersionsOfAttributes(self):

        curver = clusto.get_latest_version_number()

        e1 = Entity('e1')
        e2 = Entity('e2')

        e1.add_attr('foo', 1)
        e1.add_attr('foo2', 2)
        e1.add_attr('foo3', 3)

        SESSION.clusto_version = curver + 3

        self.assertEqual(len(list(e1.attrs)), 1)
        
        e = Entity.query().filter_by(name='e1').one()

        SESSION.clusto_version = curver + 4

        self.assertEqual(sorted([a.key for a in e.attrs]),
                         sorted(['foo', 'foo2']))


    def testAttributesImmutable(self):

        e1 = Entity('e1')
        e1.add_attr('foo', 1)

        a = e1.attrs[0]

        self.assertRaises(Exception, setattr, a.value, 2)

        
    def testEntityImmutable(self):

        e1 = Entity('e1')

        self.assertRaises(Exception, setattr, e1.driver, 'foo')

    def testEntityRename(self):

        curver = clusto.get_latest_version_number()

        e1 = Entity('e1')

        e1.add_attr('foo',1)
        e1.add_attr('foo',2)

        e1attrs = [a.to_tuple for a in e1.attrs]
        
        midver = clusto.get_latest_version_number()

        clusto.rename('e1', 't1')

        postrenamever = clusto.get_latest_version_number()
        
        t1 = clusto.get_by_name('t1')

        self.assertEqual(sorted(e1attrs),
                         sorted([a.to_tuple for a in t1.entity.attrs]))

        
        t1.del_attrs('foo', 2)

        self.assertRaises(LookupError, clusto.get_by_name, 'e1')

        self.assertEqual(sorted(t1.attrs('foo',1)),
                         sorted(t1.attrs()))

        SESSION.clusto_version = midver

        self.assertRaises(LookupError, clusto.get_by_name, 't1')

        e = clusto.get_by_name('e1')

        self.assertEqual(sorted(e1attrs),
                         sorted([a.to_tuple for a in e.attrs()]))

        
        for a in e.attrs():
            self.assertEqual(e.entity.deleted_at_version,
                             a.deleted_at_version)

        SESSION.clusto_version = postrenamever

        self.assertEqual(e.entity.deleted_at_version,
                         t1.entity.version)

        for a in t1.attrs():
            self.assertEqual(e.entity.deleted_at_version,
                             a.version)
