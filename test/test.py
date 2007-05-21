
import testbase
import unittest

from schema import *


class TestThingSchema(unittest.TestCase):

    def setUp(self):
        
        metadata.connect('sqlite:///:memory:')
        metadata.create_all()



    def tearDown(self):

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
        


if __name__ == '__main__':
    #unittest.main()
    suite = unittest.makeSuite(TestThingSchema)
    unittest.TextTestRunner(verbosity=2).run(suite)

