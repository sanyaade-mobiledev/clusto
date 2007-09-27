import unittest
import testbase

import clusto
from clusto.drivers.Base import *
from clusto.drivers.Servers import *

class TestClusto(testbase.ClustoTestBase):

    def testClustoSimpleQuery(self):

        t1 = Thing('thing1')
        t1.addAttr('a', 1)
        clusto.flush()

        f1 = clusto.getByName('thing1')

        r = f1.getAttr('a')

        self.assert_(r==1)

    def testDriverList(self):

        self.assert_(len(clusto.driverlist) >= 3)

class TestClustoQuery(testbase.ClustoTestBase):
    def setUp(self):

        testbase.ClustoTestBase.setUp(self)
        
        t1 = Thing('tp')
        t2 = Thing('t2')
        t3 = Thing('t3')
        t4 = Server('t4')
        t5 = Server('t5')

        t2.addAttr('attr1', '1')
        t2.addAttr('attr2', '2')

        t4.addAttr('attr1', '1')
        t4.addAttr('attr2', '2')
        t4.addAttr('attr4', '4')

        t5.addAttr('attr2', '2')
        t5.addAttr('attr3', '3')
        t5.addAttr('attr4', '4')
        
        
        # part
        tp1 = Part('tp1')
        tp2 = Part('tp2')
        tp3 = Part('tp3')

        t1.connect(t2)
        t1.connect(tp1)
        tp1.connect(t3)
        tp1.connect(tp2)
        tp2.connect(t4)
        
        clusto.flush()

        

    def testTypeQuery(self):

        result = clusto.query(ofTypes=[Server])

        self.assert_(set([i.name for i in result]) == set(['t4', 't5']))

        result = clusto.query(ofTypes=[Server, Part])

        self.assert_(len(result) == 5)

        result = clusto.query(ofTypes=[[Part,Thing]])

        self.assert_(len(result) == 3)

        result = clusto.query(ofTypes=[[Server]])

        self.assert_(set([i.name for i in result]) == set(['t4', 't5']))

        result = clusto.query(ofTypes=[Thing])

        self.assert_(len(result) == 8)

        


    def testNamesQuery(self):

        result = clusto.query(names=['tp'])


        self.assert_(set([i.name for i in result])
                     == set(['tp']))


    
