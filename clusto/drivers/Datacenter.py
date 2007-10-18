
from clusto.drivers.Base import Thing


class Datacenter(Thing):
    """
    a datacenter
    """

    meta_attrs = {'clustotype':'datacenter'}

    required_attrs = ('location',)

class Rack(Thing):
    """
    a rack
    """

    meta_attrs = {'clustotype':'rack'}

    
    def addToRack(self, thing, ulocations):
        """
        Add a given Thing to the rack at the locations specified in the
        ulocations list.
        """

        newUs = []
        for num in ulocations:
            newUs.append(RackU(self.name + '%02d' % num,
                               unumber=num))

        for u in newUs:
            self.connect(u)
            thing.connect(u)

    def getRackContents(self):
        """
        Returns a dict of the rack contents where the U number is the key
        and the Thing occupying that U is the value.
        """

        retval = {}
        allRUs = self.getConnectedByType(RackU)

        for u in allRUs:
            retval[int(u.getAttr('unumber'))] = u.getConnectedByType(Rack,
                                                                  invert=True)[0]

        return retval
            
            


class RackU(Thing):
    """
    Rack U location
    """
    meta_attrs = {'clustotype':'rackulocation'}
    
    required_attrs = ('unumber',)

    connector = True
    
    
