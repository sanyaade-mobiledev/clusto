
from testbase import *

from clusto.drivers.Base import Thing
from clusto.drivers.Datacenter import Rack, RackU, Datacenter

class RackTests(ClustoTestBase):

    def testAddToRack(self):

        rackname = 'ashrack101'
        rack = Rack(rackname)

        t1 = Thing('foo1')

        rack.addToRack(t1, [23,24])

        clusto.flush()

        tp = clusto.getByName('foo1')

        theRack = tp.getConnectedByType(Rack)

        self.assert_(theRack[0].name == rackname)

    def testRackContents(self):

        rackname = 'ashrack101'

        rack = Rack(rackname)

        t1 = Thing('t1')
        t2 = Thing('t2')
        t3 = Thing('t3')

        rack.addToRack(t3, [1,2])
        rack.addToRack(t2, [32])
        rack.addToRack(t1, [23,24,25])

        clusto.flush()

        contents = rack.getRackContents()

        self.assert_(contents[1].name == contents[2].name =='t3')
        self.assert_(contents[32].name == 't2')
        self.assert_(contents[23].name == contents[24].name
                     == contents[25].name == 't1')


    def testRackUMissingArg(self):

        # correct 
        RackU('foo2', 3)

        # missing RU number
        self.assertRaises(TypeError, RackU, 'foo') 



class Datacentertest(ClustoTestBase):
    """
    Test Datacenter Driver
    """

    def testLocationRequirement(self):

        d = Datacenter('d1', 'san francisco')
        clusto.flush()

        z = clusto.getByName('d1')

        self.assert_(z.getAttr('location') == 'san francisco')
