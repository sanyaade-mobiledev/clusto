import unittest
import testbase

import clusto
from clusto.schema import *


class TestClusto(testbase.ClustoTestBase):
    def data(self):

        Entity('e1')
        Entity('e2')
        Entity('e3')

        clusto.flush()
        
        
    def testGetByName(self):

        e1 = SESSION.query(Entity).filter_by(name='e1').one()

        q = clusto.getByName('e1')

        self.assertEqual(q, e1)

        self.assertEqual(q.name, 'e1')

    def testSimpleRename(self):

        clusto.rename('e1', 'f1')

        q = SESSION.query(Entity)

        self.assertEqual(q.filter_by(name='e1').count(), 0)

        self.assertEqual(q.filter_by(name='f1').count(), 1)
        
    

