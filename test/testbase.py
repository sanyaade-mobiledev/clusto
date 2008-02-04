import sys
import os

sys.path.insert(0, os.curdir)


import unittest

import clusto

class ClustoTestBase(unittest.TestCase):

    def data(self):
        pass
    
    def setUp(self):

        clusto.connect('sqlite:///:memory:')
        clusto.initclusto()
        self.data()


    def tearDown(self):

        clusto.clear()
        clusto.METADATA.drop_all()

