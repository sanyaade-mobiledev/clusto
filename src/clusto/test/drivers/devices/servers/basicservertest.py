
import clusto
from clusto.drivers import BasicServer, IPManager
from clusto.test import testbase

from clusto.exceptions import ResourceException

class BasicServerTest(testbase.ClustoTestBase):

    def data(self):
        s1 = BasicServer('bs1', model='7000', manufacturer='ibm')
        s2 = BasicServer('bs2', model='ab1200', manufacturer='sun')

        
    def testBasicServerCreation(self):

        s1 = clusto.getByName('bs1')
        s2 = clusto.getByName('bs2')

        self.assertEqual(s1.model, '7000')
        self.assertEqual(s1.manufacturer, 'ibm')
        self.assertEqual(s2.model, 'ab1200')
        self.assertEqual(s2.manufacturer, 'sun')

        
    def testHostname(self):

        s1 = clusto.getByName('bs1')
        s2 = clusto.getByName('bs2')

        s2.hostname = "testname"

        clusto.flush()

        self.assertEqual(s1.hostname, "bs1")

        self.assertEqual(s2.hostname, "testname")

        self.assertEqual(s2.entity.name, "bs2")

        s2.hostname = "newname"

        self.assertEqual(s2.hostname, "newname")
        

    def testFQDN(self):

        s1 = clusto.getByName('bs1')
        s2 = clusto.getByName('bs2')

        self.assertEqual(s1.FQDNs, [])

        s2.addFQDN("test.example.com")

        self.assertEqual(["test.example.com"],
                         s2.FQDNs)

        s2.addFQDN("test2.example.com")
        
        clusto.flush()

        self.assertEqual(sorted(["test.example.com",
                                 "test2.example.com"]),
                         sorted(s2.FQDNs))

        s2.removeFQDN("test.example.com")

        
        self.assertEqual(["test2.example.com"],
                         s2.FQDNs)


    def testAddingIP(self):

        s1 = clusto.getByName('bs1')

        self.assertRaises(ResourceException, s1.addIP, '10.0.0.100')

        ipm = IPManager('ipman', netmask='255.255.0.0', baseip='10.0.0.1')

        s1.addIP('10.0.0.100')
        
        self.assertTrue(s1.hasIP('10.0.0.100'))

        s1.addIP(ipman=ipm)

        self.assertTrue(s1.hasIP('10.0.0.1'))

    def testAddingIPfromIPManagerWithGateway(self):
                        
        s1 = clusto.getByName('bs1')
        ipm = IPManager('ipman', netmask='255.255.0.0', baseip='10.0.0.1', gateway='10.0.0.1')

        s1.addIP(ipman=ipm)

        self.assertTrue(s1.hasIP('10.0.0.2'))
        
