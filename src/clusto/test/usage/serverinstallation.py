
from clusto.test import testbase

from clusto.drivers import BasicServer, BasicRack, IPManager
from clusto.drivers import BasicNetworkSwitch, BasicPowerStrip
from clusto.exceptions import ConnectionException
import clusto

class ServerInstallationTest(testbase.ClustoTestBase):
    """Test installing a server 

    Put the server into a rack 
    connect the server to a powerstrip and a networkswitch
    """

    def data(self):
        
        r1 = BasicRack('r1')
        
        sw1 = BasicNetworkSwitch('sw1')

        s1 = BasicServer('s1')
        
        p1 = BasicPowerStrip('p1')

        r1.insert(p1, (10,11))
        r1.insert(sw1, 12)
        r1.insert(s1, 1)

    def testServerRackLocation(self):

        r = clusto.get_by_name('r1')
        s = clusto.get_by_name('s1')
        
        self.assertEqual(BasicRack.get_rack_and_u(s)['RU'], [1])

        self.assertEqual(r.getDeviceIn(12),
                         clusto.get_by_name('sw1'))

        self.assertEqual(r.getDeviceIn(10),
                         clusto.get_by_name('p1'))

        self.assertEqual(r.getDeviceIn(11),
                         clusto.get_by_name('p1'))
        
        

    def testPortConnections(self):

        s = clusto.get_by_name('s1')
        sw = clusto.get_by_name('sw1')
        p1 = clusto.get_by_name('p1')

        sw.connect_ports('nic-eth', 0, s, 0)
        
        
        self.assertRaises(ConnectionException,
                          s.connect_ports, 'nic-eth', 0, sw, 1)

        p1.connect_ports(porttype='pwr-nema-5',
                        srcportnum=0,
                        dstdev=s,
                        dstportnum=0)
                        
        self.assertEqual(s.get_connected('pwr-nema-5', 0),
                         p1)


    def testSettingUpServer(self):
        
        from clusto.drivers import SimpleEntityNameManager

        servernames = SimpleEntityNameManager('servernames',
                                              basename='server',
                                              digits=4
                                              )

        newserver = servernames.allocate(BasicServer)
        

        sw = clusto.get_by_name('sw1')
        p1 = clusto.get_by_name('p1')
        r = clusto.get_by_name('r1')

        self.assertEqual('server0001', newserver.name)


        self.assertRaises(TypeError, r.insert, newserver, 1)

        r.insert(newserver,2)
        p1.connect_ports('pwr-nema-5', 0, newserver, 0)
        sw.connect_ports('nic-eth', 0, newserver, 0)
        sw.connect_ports('nic-eth', 2, p1, 0)

        self.assertEqual(BasicRack.get_rack_and_u(newserver)['rack'], r)

        ipman = IPManager('subnet-10.0.0.1', netmask='255.255.255.0', basip='10.0.0.1')
        newserver.bind_ip_to_osport('10.0.0.10', 'eth0', porttype='nic-eth', portnum=0)

        ipvals = newserver.attrs(value='10.0.0.10')
        self.assertEqual(len(ipvals), 1)

        self.assertEqual(ipvals[0].value, '10.0.0.10')

        self.assertEqual(clusto.get_by_attr('ip', '10.0.0.10'), [newserver])
