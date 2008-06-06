
import clusto
from clusto.drivers import BasicRack, BasicServer
import testbase

class BasicRackTest(testbase.ClustoTestBase):

    def data(self):

        r1 = BasicRack('r1')

        clusto.flush()

    def testAddingToRack(self):

        r1 = clusto.getByName('r1')

        s1 = BasicServer('s1')

        r1.addDevice(s1, 1)

        clusto.flush()

        st = clusto.getByName('s1')

        a = list(st.references(key='RU', numbered=True,
                               clustotype=BasicRack._clustoType))

        self.assertEqual(len(a), 1)

        self.assertEqual(a[0].entity.name, 'r1')

        
        
