import unittest
#from clusto.schema import *
import clusto
from clusto.drivers.Servers import *
import testbase

class TestServer(testbase.ClustoTestBase):


    def testServerObject(self):

        s1 = Server('serv1')

        print [i.name for i in Server.query()]
        clusto.flush()

        
        s = clusto.getByName('serv1')

        self.assertEqual("\n".join(["serv1.clustotype server"]),
                         str(s))


        self.assert_(isinstance(s, Server))
        
