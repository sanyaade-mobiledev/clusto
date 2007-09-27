import sys
sys.path.insert(0, './src/lib/')
sys.path.insert(1, './tests')


import unittest

import clusto

class ClustoTestBase(unittest.TestCase):

    def setUp(self):
        
        clusto.METADATA.connect('sqlite:///:memory:')
        clusto.METADATA.create_all()



    def tearDown(self):

        clusto.CTX.current.clear()
        clusto.METADATA.dispose()
