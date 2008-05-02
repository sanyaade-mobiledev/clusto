from clusto.drivers.Base import ResourceManager

class SimpleNameManager(ResourceManager):

    _driverName = "simplenamemanager"
    _properties = ('basename', 'digits', 'next', 'incrementForever')

    def __init__(self, name=None, entity=None,
                 basename='',
                 digits=2,
                 incrementForever=True,
                 *args, **kwargs):


        super(ResourceManager, self).__init__(name=name, entity=entity,
                                              *args, **kwargs)
        
        self.basename = basename
        self.digits = digits
        self.incrementForever = incrementForever
        self.next = 0

    def allocator(self):

        if self.incrementForever:
            num = self.next
        else:
            # use the first open slot
            num = 0
            for attr in self.attrs(key=self.basename):
                cur = int(attr.key.replace(self.basename, '', 1))
                if cur == num:
                    num += 1
                else:
                    num = cur
                    break
                        
        nextname = self.basename + str(num).rjust(self.digits, '0')
        return nextname
        
    
    def createEntity(self, clustotype, *args, **kwargs):
        """
        Create an entity with a name generated from this NameResource
        """

        name = self.allocator()

        return clustotype(name=name, *args, **kwargs)


