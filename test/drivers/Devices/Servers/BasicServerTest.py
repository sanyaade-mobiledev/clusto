
import clusto
from clusto.drivers import BasicServer
import testbase

class BasicServerTest(testbase.ClustoTestBase):

    def data(self):
        s1 = BasicServer('bs1', model='7000', manufacturer='ibm')
        s2 = BasicServer('bs2', model='ab1200', manufacturer='sun')

        clusto.flush()
        
    def testBasicServerCreation(self):

        s1 = clusto.getByName('bs1')
        s2 = clusto.getByName('bs2')

        self.assertEqual(s1.model, '7000')
        self.assertEqual(s1.manufacturer, 'ibm')
        self.assertEqual(s2.model, 'ab1200')
        self.assertEqual(s2.manufacturer, 'sun')

        
        

        
