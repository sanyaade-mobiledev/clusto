import unittest
from clusto.test import testbase

import clusto
from clusto.schema import *
from clusto.drivers.base import *
from clusto.drivers import BasicDatacenter
from sqlalchemy.exceptions import InvalidRequestError

class TestClusto(testbase.ClustoTestBase):
    def data(self):

        Entity('e1')
        Entity('e2')
        Entity('e3')

        clusto.flush()
        

    def testClustoMeta(self):

        cm = clusto.getByName('clustometa')

        self.assertEqual(cm.version, VERSION)
        
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

    def testTransactionRollback3(self):

        d1 = Entity('d1')

        clusto.beginTransaction()
        d2 = Entity('d2')
        clusto.rollbackTransaction()

        clusto.getByName('d1')
        self.assertRaises(LookupError, clusto.getByName, 'd2')

    def testTransactionRollback4(self):

        d1 = Driver('d1')

        try:
            clusto.beginTransaction()

            d2 = Driver('d2')

            try:
                clusto.beginTransaction()
                d2.addAttr('foo', 'bar')

                clusto.commit()
            
            except:
                clusto.rollbackTransaction()

            d1.addAttr('foo2', 'bar2')

            raise Exception()
            clusto.commit()
        except:
            clusto.rollbackTransaction()

        self.assertEqual(d1.attrs(), [])
        self.assertRaises(LookupError, clusto.getByName, 'd2')
            

    def testTransactionCommit(self):

        try:
            clusto.beginTransaction()
            
            c1 = Entity('c1')
            clusto.commit()
        except Exception:
            clusto.rollbackTransaction()

        clusto.getByName('c1')


    def testGetEntities(self):

        d1 = Driver('d1')
        dv1 = Device('dv1')
        Location('l1')
        BasicDatacenter('dc1')

        
        namelist = ['e1', 'e2', 'dv1']

        self.assertEqual(sorted([n.name 
                                 for n in clusto.getEntities(names=namelist)]),
                         sorted(namelist))

        dl = [Driver]
        self.assertEqual(sorted([n.name
                                 for n in clusto.getEntities(clustoDrivers=dl)]),
                         sorted(['d1','e1','e2','e3']))


        tl = [Location, BasicDatacenter]
        self.assertEqual(sorted([n.name
                                 for n in clusto.getEntities(clusto_types=tl)]),
                         sorted(['l1','dc1']))

    def testGetEntitesWithAttrs(self):

        d1 = Driver('d1')
        d2 = Driver('d2')
        d3 = Driver('d3')
        d4 = Driver('d4')

        d1.addAttr('k1', 'test')
        d2.addAttr('k1', 'testA')

        d1.addAttr('k2', number=1, subkey='A', value=67)
        d3.addAttr('k3', number=True, value=d4)



        self.assertEqual(clusto.getEntities(attrs=[{'key':'k2'}]),
                         [d1])


        self.assertEqual(sorted(clusto.getEntities(attrs=[{'key':'k1'}])),
                         sorted([d1,d2]))


        self.assertEqual(sorted(clusto.getEntities(attrs=[{'value':d4}])),
                         [d3])


        self.assertEqual(clusto.getEntities(attrs=[{'value':67}]),
                         [d1])

        self.assertEqual(sorted(clusto.getEntities(attrs=[{'number':0}])),
                         sorted([d3]))

        self.assertEqual(clusto.getEntities(attrs=[{'subkey':'A'},
                                                   {'value':'test'}]),
                         [d1])

    def testDeleteEntity(self):

        e1 = SESSION.query(Entity).filter_by(name='e1').one()

        d = Driver(e1)

        d.addAttr('deltest1', 'test')
        d.addAttr('deltest1', 'testA')



        clusto.deleteEntity(e1)


        self.assertEqual([], clusto.getEntities(names=['e1']))

        self.assertEqual([], Driver.doAttrQuery(key='deltest*', glob=True))
                         


