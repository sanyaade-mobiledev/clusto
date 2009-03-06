
import clusto
from clusto.drivers import BasicServer, IPManager
from clusto.test import testbase

from clusto.exceptions import ResourceException, ResourceLockException

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


    def testBindingIPtoPortWithNoIPManager(self):

        s1 = clusto.getByName('bs1')

        self.assertRaises(ResourceException, s1.bindIPtoPort, '192.168.1.20', 'nic-eth', 1)


    def testBindingIPtoPort(self):

        s1 = clusto.getByName('bs1')

        ipm = IPManager('ipman', netmask='255.255.255.0', baseip='192.168.1.0')

        s1.bindIPtoPort('192.168.1.20', 'nic-eth', 1)

        self.assertRaises(ResourceLockException, ipm.deallocate, s1, '192.168.1.20')
        

    def testUnBindingIPFromPort(self):

        s1 = clusto.getByName('bs1')

        ipm = IPManager('ipman', netmask='255.255.255.0', baseip='192.168.1.0')

        s1.bindIPtoPort('192.168.1.20', 'nic-eth', 1)

        s1.unbindIPfromPort('192.168.1.20', 'nic-eth', 1)

        ipm.deallocate(s1, '192.168.1.20')

    
        
