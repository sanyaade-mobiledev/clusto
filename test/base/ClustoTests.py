import unittest

import clusto
from clusto.drivers.Servers import *

class TestClusto(unittest.TestCase):

    def setUp(self):
        
        clusto.METADATA.connect('sqlite:///:memory:')
        clusto.METADATA.create_all()



    def tearDown(self):

        clusto.CTX.current.clear()
        clusto.METADATA.dispose()

    def testClustoQuery(self):
        pass


    
