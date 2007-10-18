from clusto.drivers.Base import Thing, Part, Resource
import clusto

class HeirarchyMixin:
    """
    Give heirarchical functionality to a Thing
    """

    def setParent(self, something):

        if self.hasParent():
            self.removeParent()
            
        self.setAttrs('_parent', [something.name])
        self.connect(something)

        something.addAttr('_child', self.name)
        
    def removeParent(self):

        if not self.hasParent():
            return # maybe raise an exception here
        else:
            parent = self.getParent()
            
            self.delAttr('_parent', parent.name)
            self.disconnect(parent)


    def addChild(self, something):

        something.setParent(self)

    def removeChild(self, something):

        self.delAttr('_child', something.name)
        self.disconnect(something)
    
    def getParent(self, allparents=False):

        if self.hasParent():
            parentname = self.getAttr('_parent', justone=True)
            parent =  clusto.getByName(parentname)
            if not allparents:
                return parent
            else:
                ## fix here
                l = [parent]
                while not parent.isTopParent():
                    parent = parent.getParent()
                    l.insert(0, parent)
                return l
        else:
            return None # maybe raise exception instead
        

    def getChildren(self):

        childnames = self.getAttr('_child', justone=False)
        return [clusto.getByName(i) for i in childnames]

    def isTopParent(self):

        return not self.hasAttr('_parent')

    def hasChildren(self):

        return self.hasAttr('_child')

    def hasParent(self):
        return self.hasAttr('_parent')

    def isChildOf(self, something):
        pass

    def isParentOf(self, something):
        pass
    
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


        

