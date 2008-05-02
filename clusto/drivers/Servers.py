from clusto.drivers.Base import Driver



    
class Server(Driver):
    """
    server
    """
    
    _driverName = "server"

    _properties = ('model', 'serialnumber', )

    
class VirtualServer(Driver):
    _driverName = "virtualserver"

    
    
        


