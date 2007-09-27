import sys
import os

sys.path.insert(0, os.curdir)


import unittest

import clusto

class ClustoTestBase(unittest.TestCase):

    def setUp(self):
        
        clusto.METADATA.connect('sqlite:///:memory:')
        clusto.METADATA.create_all()



    def tearDown(self):

        clusto.CTX.current.clear()
        clusto.METADATA.dispose()
