
from Base import Thing

    
class LoadBalancer(Thing):
    meta_attrs = { 'clustotype': 'loadbalancer' }



class OpenGearLoadBalancer(LoadBalancer):
    meta_attrs = { 'vendor': 'opengear' }
    

class Netscaler(LoadBalancer):

    meta_attrs = { 'vendor': 'citrix' }




class Class(Thing):
    """
    A Class is used to identify the configuration of a Thing, usually
    a server.

    For example, servers connected to the 'mysqlserver' class would
    have the mysql server related packages and configurations installed
    """
    meta_attrs = { 'clustotype': 'class' }

class Role(Thing):
    """
    A Role is used to identify the job of a Thing.

    For example, a server connected to the 'dbslave' role will have the
    job of acting as a database slave in a master/slaves configuration.
    """
    meta_attrs = { 'clustotype': 'role' }

class Service(Thing):
    """
    A Service is used to identify an instance of a role.

    For example, dbslave01, dbslave02... 
    """
    meta_attrs = { 'clustotype': 'service' }

class Cluster(Thing):
    """
    A Cluster is used to identify a group of Things.  

    For example, several servers can be connected to the 'production' cluster
    to signify that they all be used in the production environment.
    """
    meta_attrs = { 'clustotype': 'cluster' }

    
class Defaults(Thing):

    meta_attrs = { 'clustotype': 'defaults' }

