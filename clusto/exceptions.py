
class DriverException(Exception):
    """exception for driver errors"""
    pass

class ConnectionException(Exception):
    """exception for operations related to connecting two Things together"""
    pass


class NameException(Exception):
    """exception for invalid entity or attribute names"""
    pass


class ResourceException(Exception):
    """exception related to resources"""
    pass

class ResourceNotAvailableException(ResourceException):
    pass

class ResourceTypeException(ResourceException):
    pass

