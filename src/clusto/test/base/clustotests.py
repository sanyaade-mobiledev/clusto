import unittest
from clusto.test import testbase

import clusto
from clusto.schema import *
from clusto.drivers.base import *
from clusto.drivers import BasicDatacenter
from sqlalchemy.exceptions import InvalidRequestError

class TestClustoPlain(testbase.ClustoTestBase):

    def testInitClustoIdempotent(self):
        
        clusto.init_clusto()
        clusto.init_clusto()
        clusto.init_clusto()
        clusto.init_clusto()

        self.assertEqual(SESSION.query(ClustoVersioning).count(), 3)
                                       


class TestClusto(testbase.ClustoTestBase):
    def data(self):

        Entity('e1')
        Entity('e2')
        Entity('e3')

        clusto.flush()
        

    def testClustoMeta(self):

        cm = clusto.get_by_name('clustometa')

        self.assertEqual(cm.schemaversion, VERSION)
        
    def testGetByName(self):

        e1 = SESSION.query(Entity).filter_by(name='e1').one()

        q = clusto.get_by_name('e1')

        self.assertEqual(q, e1)

        self.assertEqual(q.name, 'e1')

    def testSimpleRename(self):

        clusto.rename('e1', 'f1')

        q = SESSION.query(Entity)

        self.assertEqual(q.filter_by(name='e1').count(), 0)

        self.assertEqual(q.filter_by(name='f1').count(), 1)
        
    

    def testTransactionRollback(self):

        clusto.begin_transaction()
        
        d1 = Entity('d1')

        clusto.get_by_name('d1')

        d2 = Entity('d2')
        clusto.rollback_transaction()


        self.assertRaises(LookupError, clusto.get_by_name, 'd1')

    def testTransactionRollback2(self):

        try:
            clusto.begin_transaction()

            c1 = Entity('c1')
            
            raise Exception()
        except Exception:
            
            clusto.rollback_transaction()

        c2 = Entity('c2')
        
        self.assertRaises(LookupError, clusto.get_by_name, 'c1')
        clusto.get_by_name('c2')

    def testTransactionRollback3(self):

        d1 = Entity('d1')

        clusto.begin_transaction()
        d2 = Entity('d2')
        clusto.rollback_transaction()

        clusto.get_by_name('d1')
        self.assertRaises(LookupError, clusto.get_by_name, 'd2')

    def testTransactionRollback4(self):

        d1 = Driver('d1')

        try:
            clusto.begin_transaction()

            d2 = Driver('d2')

            try:
                clusto.begin_transaction()
                d2.add_attr('foo', 'bar')

                clusto.commit()
            
            except:
                clusto.rollback_transaction()

            d1.add_attr('foo2', 'bar2')

            raise Exception()
            clusto.commit()
        except:
            clusto.rollback_transaction()

        self.assertEqual(d1.attrs(), [])
        self.assertRaises(LookupError, clusto.get_by_name, 'd2')
            

    def testTransactionCommit(self):

        try:
            clusto.begin_transaction()
            
            c1 = Entity('c1')
            clusto.commit()
        except Exception:
            clusto.rollback_transaction()

        clusto.get_by_name('c1')


    def testGetEntities(self):

        d1 = Driver('d1')
        dv1 = Device('dv1')
        Location('l1')
        BasicDatacenter('dc1')

        
        namelist = ['e1', 'e2', 'dv1']

        self.assertEqual(sorted([n.name 
                                 for n in clusto.get_entities(names=namelist)]),
                         sorted(namelist))

        dl = [Driver]
        self.assertEqual(sorted([n.name
                                 for n in clusto.get_entities(clusto_drivers=dl)]),
                         sorted(['d1','e1','e2','e3']))


        tl = [Location, BasicDatacenter]
        self.assertEqual(sorted([n.name
                                 for n in clusto.get_entities(clusto_types=tl)]),
                         sorted(['l1','dc1']))

    def testGetEntitesWithAttrs(self):

        d1 = Driver('d1')
        d2 = Driver('d2')
        d3 = Driver('d3')
        d4 = Driver('d4')

        d1.add_attr('k1', 'test')
        d2.add_attr('k1', 'testA')

        d1.add_attr('k2', number=1, subkey='A', value=67)
        d3.add_attr('k3', number=True, value=d4)



        self.assertEqual(clusto.get_entities(attrs=[{'key':'k2'}]),
                         [d1])


        self.assertEqual(sorted(clusto.get_entities(attrs=[{'key':'k1'}])),
                         sorted([d1,d2]))


        self.assertEqual(sorted(clusto.get_entities(attrs=[{'value':d4}])),
                         [d3])


        self.assertEqual(clusto.get_entities(attrs=[{'value':67}]),
                         [d1])

        self.assertEqual(sorted(clusto.get_entities(attrs=[{'number':0}])),
                         sorted([d3]))

        self.assertEqual(clusto.get_entities(attrs=[{'subkey':'A'},
                                                   {'value':'test'}]),
                         [d1])

    def testDeleteEntity(self):

        e1 = SESSION.query(Entity).filter_by(name='e1').one()

        d = Driver(e1)

        d.add_attr('deltest1', 'test')
        d.add_attr('deltest1', 'testA')



        clusto.delete_entity(e1)


        self.assertEqual([], clusto.get_entities(names=['e1']))

        self.assertEqual([], Driver.do_attr_query(key='deltest*', glob=True))
                         


