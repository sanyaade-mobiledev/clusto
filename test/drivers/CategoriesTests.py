
import clusto
import testbase 
import itertools

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

    def testGetPools(self):

        d1, d2, p1 = [clusto.getByName(i) for i in ['d1', 'd2', 'p1']]

        p2 = Pool('p2')
        
        p1.addToPool(d1)
        p2.addToPool(d1)
        p1.addToPool(d2)


        self.assertEqual(sorted(Pool.getPools(d1)),
                         sorted([p1,p2]))

    def testGetPoolsMultiLevel(self):

        d1, d2, p1 = [clusto.getByName(i) for i in ['d1', 'd2', 'p1']]

        p2 = Pool('p2')
        p3 = Pool('p3')
        p4 = Pool('p4')
        d3 = Driver('d3')
        
        p1.addToPool(d1)
        p2.addToPool(d1)
        p1.addToPool(d2)

        p1.addToPool(p3)
        p3.addToPool(p4)
        p4.addToPool(d3)

        self.assertEqual(sorted(Pool.getPools(d1, allPools=True)),
                         sorted([p1,p2]))


        self.assertEqual(sorted(set(Pool.getPools(d3, allPools=True))),
                         sorted([p1, p3, p4]))

    def testPoolsIterator(self):

        
        A = Pool('A')

        d1, d2 = [clusto.getByName(i) for i in ['d1', 'd2']]

        B = Pool('B')
        C = Pool('C')
        A1 = Pool('A1')
        B2 = Pool('B2')
        B1 = Pool('B1')
        C1 = Pool('C1')

        C1.addToPool(C)
        B1.addToPool(B)
        A1.addToPool(B)

        A1.addToPool(A)
        B2.addToPool(A)

        A.addToPool(d1)
        B.addToPool(d1)
        C.addToPool(d1)

        clusto.flush()

        self.assertEqual([x.name for x in d1.iterPools()],
                         [u'C', u'B', u'A', u'C1', u'A1', u'B1', u'B2', u'A1'])

        self.assertEqual([x.name for x in d1.iterPools(allPools=False)],
                         [u'C', u'B', u'A'])


    def testPoolAttrs(self):

        d1, d2, p1 = map(clusto.getByName, ('d1', 'd2', 'p1'))

        p1.addAttr('t1', 1)
        p1.addAttr('t2', 2)

        d1.addAttr('t3', 3)

        p1.addToPool(d1)
        p1.addToPool(d2)
        

        clusto.flush()

        d2 = clusto.getByName('d2')

        self.assertEqual(sorted(d2.attrs(mergedPoolAttrs=True)), sorted(p1.attrs()))

        #self.assertEqual(sorted(itertools.chain(d1.attrs(mergedPoolAttrs=True),
        #                                        p1.attrs(mergedPoolAttrs=True))),
        #                sorted(d1.attrs()))

        self.assertEqual(sorted(['t1', 't2', 't3']),
                         sorted([x.key for x in d1.attrs(mergedPoolAttrs=True)]))


    def testPoolAttrsOverride(self):

        d1, d2, p1 = map(clusto.getByName, ('d1', 'd2', 'p1'))

        p1.addAttr('t1', 1)
        p1.addAttr('t2', 2)

        p1.addToPool(d1)
        d1.addAttr('t1', 'foo')
        clusto.flush()

        

        
