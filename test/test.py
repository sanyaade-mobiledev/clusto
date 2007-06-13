
import testbase
import unittest

from schema import *
from drivers import *

class TestThingSchema(unittest.TestCase):

    def setUp(self):
        
        metadata.connect('sqlite:///:memory:')
        metadata.create_all()



    def tearDown(self):

        ctx.current.clear()
        metadata.dispose()


    def testThingConnections(self):
        
        t=Thing('foo1', 'newtype')
        t2=Thing('subfoo', 'subtype')
        t3=Thing('foo2', 'othertype')

        ctx.current.flush()

        ta1=ThingAssociation(t,t2)
        ta2=ThingAssociation(t3,t)

        ctx.current.flush()

        f=Thing.selectone(Thing.c.name=='foo1')

        self.assertEqual(len(f.connections), 2)

    def testDrivers(self):

        
        s1=Server('s1')
        s2=Server('s2')

        t1=Thing('t1', 'foo')
        t2=Thing('t2', 'foo')

        self.assertEqual(s1.thingtype, 'server')
                                 
        ctx.current.flush()

        l=Server.select()
        
        self.assertEqual(len(l), 2)

        o=Thing.select()
        self.assertEqual(len(o), 4)
        ctx.current.flush()
        
    def testAttributes(self):

        s1=Server('s4')
        
        ctx.current.flush()
        
        s=Server.selectone(Server.c.name=='s4')

        s.attrs.append(Attribute('g',1))
        s.attrs['a'] = 2
        s.attrs['b'] = 3
        
        ctx.current.flush()        

        self.assertEqual(s.attrs['driver'], 'Server')
        a = Attribute.select()
        self.assertEqual(len(a), 4)

        n1 = Netscaler('one1')

        self.assertEqual(n1.attrs['vendor'], 'citrix')
        ctx.current.flush()

    def testOutput(self):

        s1 = Server('s5')
        s1.attrs['version'] = 1
        s1.attrs['model'] = 'amd'
        
        s2 = Server('s6')
        s2.attrs['version'] = 2
        s2.attrs['vender'] = 'penguin computing'
        s1.connect(s2)
        
        print s1
        print s2
        
if __name__ == '__main__':
    suite = unittest.makeSuite(TestThingSchema)
    unittest.TextTestRunner(verbosity=2).run(suite)
    
