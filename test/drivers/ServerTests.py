import unittest
#from clusto.schema import *
import clusto
from clusto.drivers.Servers import *

class TestServer(unittest.TestCase):

    def setUp(self):
        
        clusto.METADATA.connect('sqlite:///:memory:')
        clusto.METADATA.create_all()



    def tearDown(self):

        clusto.CTX.current.clear()
        clusto.METADATA.dispose()


    def testServerObject(self):

        s1 = Server('serv1')

        
        clusto.flush()

        
        s = Thing.selectone(Thing.c.name=='serv1')

        self.assertEqual("\n".join(["serv1.clustotype server",
                                    ""]),
                         str(s))


        self.assert_(isinstance(s, Server))
        
