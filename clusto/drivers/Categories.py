from clusto.drivers.Base import Thing, Part, Resource
from clusto.drivers.Mixins import HeirarchyMixin
import clusto
    
class Class(Resource):
    meta_attrs = {'clustotype':'class'}
    
class Role(Resource):
    meta_attrs = {'clustotype':'role'}

class Pool(Resource, HeirarchyMixin):
    meta_attrs = {'clustotype':'pool'}

    @classmethod
    def getPools(cls, something):
        """
        Find what Pools the given Thing is contained in.

        Return array of Pools sorted by heirarchy with the Pool at the top of
        the tree listed first in the array.

        """

        allpools = []
        # get most closely connected pool
        closepool = something.getConnectedByType(cls)

        allpools.append(closepool)

        currentpool = closepool
        while True:
            pass #if currentpool.has


        

