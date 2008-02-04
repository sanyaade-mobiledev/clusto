import clusto

class HeirarchyMixin:
    """
    Give heirarchical functionality to a Thing
    """

    def setParent(self, something):

        if self.hasParent():
            self.removeParent()
            
        self.setAttrs('_ref_parent', [something.name])
        self.connect(something)

        something.addAttr('_ref_child', self.name)

    def removeParent(self):

        if not self.hasParent():
            return # maybe raise an exception here
        else:
            parent = self.getParent()
            
            self.delAttr('_ref_parent', parent.name)
            self.disconnect(parent)


    def addChild(self, something):

        self.connect(something)
        something.setAttrs('_ref_parent', [self.name])
        self.addAttr('_ref_child', something.name)
        
        
    def removeChild(self, something):

        self.delAttr('_ref_child', something.name)
        something.delAttrs('_ref_parent')
        self.disconnect(something)

    def getParent(self, allparents=False):

        if self.hasParent():
            parentname = self.getAttr('_ref_parent', justone=True)
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

        childnames = self.getAttr('_ref_child', justone=False)
        return [clusto.getByName(i) for i in childnames]

    def isTopParent(self):

        return not self.hasAttr('_ref_parent') and self.hasChildren()

    def hasChildren(self):

        return self.hasAttr('_ref_child')


    def hasParent(self):
        return self.hasAttr('_ref_parent')

    def isChildOf(self, something):
        parent = self.getParent()
        return parent == something

    def isParentOf(self, something):

        return something.name in [x.name for x in self.getChidren()]

class LocationMixin(HeirarchyMixin):

    def __contains__(self, something):
        return self.isParentOf(something)
    
    def insert(self, something):
        self.addChild(something)

    def remove(self, something):
        self.removeChild(something)

        
