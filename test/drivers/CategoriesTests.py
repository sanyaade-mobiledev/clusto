
from testbase import *

from clusto.drivers.Base import Thing
from clusto.drivers.Categories import Pool

class PoolTests(ClustoTestBase):

    def testChildren(self):

        p1 = Pool('p1')
        p2 = Pool('p2')
        p3 = Pool('p3')
        p4 = Pool('p4')
        
        p1.addChild(p2)

        p2.addChild(p3)
        p2.addChild(p4)

        clusto.flush()

        children = [i.name for i in p2.getChildren()]

        self.assert_(p3.name in children)
        self.assert_(p4.name in children)

    def testParent(self):
        p1 = Pool('p1')
        p2 = Pool('p2')
        p3 = Pool('p3')
        p4 = Pool('p4')
        
        p1.addChild(p2)

        p2.addChild(p3)
        p2.addChild(p4)

        clusto.flush()

        p = clusto.getByName('p4')

        self.assertEquals(p2.name, p.getParent().name)

        self.assertEquals([u'p1', u'p2'],
                          [i.name for i in p.getParent(allparents=True)])

        self.assertFalse(p4.isTopParent())
