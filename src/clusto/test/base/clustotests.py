import unittest
from clusto.test import testbase

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
        
    

    def testTransactionRollback(self):

	clusto.beginTransaction()
	
	d1 = Entity('d1')

	clusto.getByName('d1')

	d2 = Entity('d2')
	clusto.rollbackTransaction()


	self.assertRaises(LookupError, clusto.getByName, 'd1')

    def testTransactionRollback2(self):

	try:
	    clusto.beginTransaction()

	    c1 = Entity('c1')
	    
	    raise Exception()
	except Exception:
	    
	    clusto.rollbackTransaction()

	c2 = Entity('c2')
	
	self.assertRaises(LookupError, clusto.getByName, 'c1')
	clusto.getByName('c2')

    def testTransactionCommit(self):

	try:
	    clusto.beginTransaction()
	    
	    c1 = Entity('c1')
	    clusto.commit()
	except Exception:
	    clusto.rollbackTransaction()

	clusto.getByName('c1')

