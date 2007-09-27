from Base import Part

class Port(Part):
    meta_attrs = {'clustotype': 'port'}

    required_attrs = ('portnum',)

    connector = True

    def canConnectTo(self, something):

        return not something.isOfType(Port)
    

    

