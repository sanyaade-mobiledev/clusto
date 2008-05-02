import clusto
import testbase 
import itertools

from clusto.drivers import *

class NameResourceTests(testbase.ClustoTestBase):

    def data(self):

        n1 = SimpleNameManager(name='foonamegen',
                               basename='foo',
                               digits=4,
                               )


        clusto.flush()

    def testAllocateName(self):

        ngen = clusto.getByName('foonamegen')

        
        
                                    
