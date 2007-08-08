
from clusto.drivers.Base import Thing
from clusto.schema import *

class Clusto:

        
    @classmethod
    def query(self, matchdicts, notdicts):
        """
        Query clusto for Things.

        
        """
        
        pass

    @classmethod
    def save(self):
        """
        Save all the changes to objects.
        """
        CTX.current.flush()
                
