
import clusto
import testbase 

from clusto.drivers import *


class PoolTests(testbase.ClustoTestBase):

    def data(self):

        d1 = Driver('d1')
        d2 = Driver('d2')

        p1 = Pool('p1')

        clusto.flush()


    def testPoolCreate(self):

        p3 = Pool('p3')
        d3 = Driver('d3')
        
        clusto.flush()

        q = clusto.getByName('p3')

        self.assertTrue(isinstance(q, Pool))

        self.assertFalse(isinstance(clusto.getByName('d3'), Pool))

    def testPoolMembers(self):

        d1, d2, p1 = map(clusto.getByName, ('d1', 'd2', 'p1'))
        
        p1.addToPool(d1)
        p1.addToPool(d2)
        
        clusto.flush()


        q = clusto.getByName('p1')


        membernames = sorted([x.name for x in q.members])

        self.assertEqual(membernames, sorted(['d1','d2']))

    def testPoolMixin(self):

        d1, d2, p1 = map(clusto.getByName, ('d1', 'd2', 'p1'))

        self.assertTrue(hasattr(d1, 'pools'))

    def testPoolAttrs(self):

        d1, d2, p1 = map(clusto.getByName, ('d1', 'd2', 'p1'))

        p1.addAttr('t1', 1)
        p1.addAttr('t2', 2)

        d1.addAttr('t3', 3)

        p1.addToPool(d1)
        p1.addToPool(d2)
        

        clusto.flush()

        d2 = clusto.getByName('d2')

        self.assertEqual(sorted(d2.attrs()), sorted(p1.attrs()))

        self.assertEqual(sorted(d1.attrs(onlyLocal=True)
                               +p1.attrs(onlyLocal=True)),
                        sorted(d1.attrs()))

        self.assertEqual(sorted(['t1', 't2', 't3']),
                         sorted([x.key for x in d1.attrs()]))

    def testMultiLevelPoolAttrs(self):

        p2 = Pool('p2')
        p3 = Pool('p3')

        d1, d2, p1 = map(clusto.getByName, ('d1', 'd2', 'p1'))

        p1.addAttr('t1', 1)
        p2.addAttr('t2', 2)
        p3.addAttr('t3', 3)
        p1.addToPool(p2)
        p2.addToPool(p3)
        p2.addToPool(d1)
        p3.addToPool(d2)

        clusto.flush()

        self.assertEqual(sorted(['t1', 't2', 't3']),
                         sorted([x.key for x in d2.attrs()]))

        self.assertEqual(sorted(p2.attrs()),
                         sorted(d1.attrs()))


        self.assertEqual(len(d2.attrs()), 3)

        
