import unittest

import clusto
from clusto.drivers.Base import *
from clusto.drivers.Servers import *

class TestClusto(unittest.TestCase):

    def setUp(self):
        
        clusto.METADATA.connect('sqlite:///:memory:')
        clusto.METADATA.create_all()



    def tearDown(self):

        clusto.CTX.current.clear()
        clusto.METADATA.dispose()

    def testClustoSimpleQuery(self):

        t1 = Thing('thing1')
        t1.addAttr('a', 1)
        clusto.flush()

        f1 = clusto.getByName('thing1')

        r = f1.getAttr('a')

        self.assert_(r==1)
        
    def testClustoQuery(self):
        pass


    
