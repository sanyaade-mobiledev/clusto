
from clusto.test import testbase

from clusto.drivers import BasicServer, BasicRack
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

        r = clusto.getByName('r1')
        s = clusto.getByName('s1')
        
        self.assertEqual(BasicRack.getRackAndU(s)['RU'], [1])

        self.assertEqual(r.getDeviceIn(12),
                         clusto.getByName('sw1'))

        self.assertEqual(r.getDeviceIn(10),
                         clusto.getByName('p1'))

        self.assertEqual(r.getDeviceIn(11),
                         clusto.getByName('p1'))
        
        

    def testPortConnections(self):

        s = clusto.getByName('s1')
        sw = clusto.getByName('sw1')
	p1 = clusto.getByName('p1')

        sw.connectPorts('eth', 0, s, 0)
        
        
	self.assertRaises(ConnectionException,
			  s.connectPorts, 'eth', 0, sw, 1)

	p1.connectPorts(porttype='pwr',
			srcportnum=0,
			dstdev=s,
			dstportnum=0)
			
	self.assertEqual(s.getConnected('pwr', 0),
			 p1)


    def testSettingUpServer(self):
	
	from clusto.drivers import SimpleNameManager

	servernames = SimpleNameManager('servernames',
					basename='server',
					digits=4
					)

	newserver = servernames.createEntity(BasicServer)
	

        sw = clusto.getByName('sw1')
	p1 = clusto.getByName('p1')
        r = clusto.getByName('r1')

	self.assertEqual('server0001', newserver.name)


	self.assertRaises(TypeError, r.insert, newserver, 1)

	r.insert(newserver,2)
	p1.connectPorts('pwr', 0, newserver, 0)
	sw.connectPorts('eth', 0, newserver, 0)

	self.assertEqual(BasicRack.getRackAndU(newserver)['rack'], r)

