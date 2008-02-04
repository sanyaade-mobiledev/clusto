
from clusto.drivers.Base import Thing
from clusto.drivers.Mixins import LocationMixin
import clusto

class Datacenter(Thing, LocationMixin):
    """
    a datacenter
    """

    meta_attrs = {'clustotype':'datacenter'}

    required_attrs = ('location',)

    def canConnectTo(self, thing):
        return isinstance(thing, (Cage, Colo))
    

class Colo(Thing, LocationMixin):
    """
    a colo
    """

    meta_attrs = {'clustotype':'colo'}

    def canConnectTo(self, thing):
        return isinstance(thing, (Cage, Rack, Datacenter))
    
class Cage(Thing, LocationMixin):
    """
    a cage
    """
    meta_attrs = {'clustotype':'cage'}

    #def canConnectTo(self, thing):
    #    return isinstance(thing, [Colo, Rack, Cage, Datacenter])

class Rack(Thing, LocationMixin):
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
            newUs.append(RackU(self.name + 'u%02d' % num,
                               unumber=num))

        for u in newUs:
            u.insert(thing)
            self.insert(u)


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
            
            


class RackU(Thing, LocationMixin):
    """
    Rack U location
    """
    meta_attrs = {'clustotype':'rackulocation'}
    
    required_attrs = ('unumber',)

    connector = True
    
    
