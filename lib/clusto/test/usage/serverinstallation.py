
from clusto.test import testbase

from clusto.drivers import BasicServer, BasicRack
from clusto.drivers import BasicNetworkSwitch, BasicPowerStrip
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
        
        

    def testNetworkSwitchConnection(self):

        s = clusto.getByName('s1')
        sw = clusto.getByName('sw1')

        sw.connectPorts('eth', 0, s, 0)
        
        
	#s.connectPorts(srcporttype='eth',
	#	       srcportnum=0,
	#	       dstdev=sw,
	#	       dstporttype='eth',
	#	       dstportnum=1)
