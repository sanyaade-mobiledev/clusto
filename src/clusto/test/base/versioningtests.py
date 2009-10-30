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
        self.assertEqual(curver, 3)

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

        self.assertEqual(etest.entity.version, curver+2)


