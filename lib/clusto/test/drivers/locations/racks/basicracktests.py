
import clusto
from clusto.drivers import BasicRack, BasicServer
from clusto.test import testbase

class BasicRackTest(testbase.ClustoTestBase):

    def data(self):

        r1 = BasicRack('r1')
        r2 = BasicRack('r2')

        clusto.flush()

    def testAddingToRack(self):

        r1 = clusto.getByName('r1')

        s1 = BasicServer('s1')

        r1.addDevice(s1, 1)


        rt = clusto.getByName('r1')
        st = clusto.getByName('s1')

        a = list(st.references(key='RU', numbered=True,
                               clustotype=BasicRack._clustoType))

        self.assertEqual(len(a), 1)

        self.assertEqual(a[0].entity.name, 'r1')

    def testMaxRackPosition(self):

        r1 = clusto.getByName('r1')

        self.assertRaises(TypeError, r1.addDevice, BasicServer('s1'), 400)

        self.assertRaises(TypeError, r1.addDevice, BasicServer('s2'), -13)

        clusto.flush()

    def testGettingThingInRack(self):

        r1 = clusto.getByName('r1')

        r1.addDevice(BasicServer('s1'), 40)

        clusto.flush()

        s1 = r1.getDeviceIn(40)

        self.assertEqual(s1.name, 's1')
        

    def testGettingRackAndU(self):

        r1, r2 = [clusto.getByName(r) for r in ['r1','r2']]

        s=BasicServer('s1')
        clusto.flush()
        r1.addDevice(s, 13)

        clusto.flush()

        s = clusto.getByName('s1')

        res = BasicRack.getRackAndU(s)

        
        self.assertEqual(res['rack'].name, 'r1')
        self.assertEqual(res['RU'], [13])

        res2 = BasicRack.getRackAndU(BasicServer('s2'))
        self.assertEqual(res2, None)

    def testCanOnlyAddToOneRack(self):
        """
        A device should only be able to get added to a single rack
        """

        
        r1, r2 = [clusto.getByName(r) for r in ['r1','r2']]

        s1 = BasicServer('s1')
        s2 = BasicServer('s2')
        
        r1.addDevice(s1, 13)
        self.assertRaises(Exception, r2.addDevice,s1, 1)
        
    def testCanAddADeviceToMultipleAdjacentUs(self):
        """
        you should be able to add a device to multiple adjacent RUs
        """

        r1, r2 = [clusto.getByName(r) for r in ['r1','r2']]

        s1 = BasicServer('s1')
        s2 = BasicServer('s2')
        
        r1.addDevice(s1, [1,2,3])

        clusto.flush()

        s = clusto.getByName('s1')

        self.assertEqual(sorted(BasicRack.getRackAndU(s)['RU']),
                         [1,2,3])

        self.assertRaises(TypeError, r1.addDevice, s2, [1,2,4])

    def testAddingToDoubleDigitLocationThenSingleDigitLocation(self):

        r1, r2 = [clusto.getByName(r) for r in ['r1','r2']]

        s1 = BasicServer('s1')
        s2 = BasicServer('s2')
        
        r1.addDevice(s1, 11)

        r1.addDevice(s2, 1)

        clusto.flush()

        s = clusto.getByName('s1')

        self.assertEqual(sorted(BasicRack.getRackAndU(s)['RU']),
                         [11])

        self.assertEqual(sorted(BasicRack.getRackAndU(s2)['RU']),
                         [1])

