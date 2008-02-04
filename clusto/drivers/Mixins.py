
import re

from clusto.schema import Attribute
from clusto.exceptions import *

class AttributeListMixin:
    """
    Methods that provides functionality for working with attribute lists.
    """

    def _checkAttrName(self, key):
        """
        check to make sure the key does not contain invalid characters
        raise NameException if fail.
        """

        if not re.match('[A-Za-z_]+[0-9A-Za-z_-]*-?[A-Za-z]+[0-9A-Za-z_-]*', key):
            raise NameException("Attribute name %s is invalid. "
                                "Attribute names may not contain periods or "
                                "comas.")
    
        
    def _buildKeyName(self, key, numbered=None, subkey=None):

        keyname = key
        if numbered is not None:
            if isinstance(numbered, bool):
                number = self._getAttrNumCount(key, numbered=numbered)
            elif isinstance(numbered, int):
                number = numbered
            else:
                raise TypeError("num must be either True, or an integer.")

            keyname += str(number)

        if subkey: 
            keyname += ''.join(['-', str(subkey)])

        self._checkAttrName(keyname)

        return keyname

    def _getAttrNumCount(self, key, numbered=None):
        """
        For numbered attributes return the count that exist
        """
        attrs = self.attrs(key=key, numbered=numbered)

        return len(list(attrs))
        
    def attrs(self, key=None, value=None, numbered=None, subkey=None,
              ignoreHidden=True, strict=False):


        #if ignoreHidden:
        #    all = filter(lambda x: not x.key.startswith('_'), all)

        regex = ["^"]

        if key and key.startswith('_'):
            ignoreHidden=False
            
        if ignoreHidden:
            regex.append("(?!_)")
            
        regex.append((key and key or ".*"))

        if isinstance(numbered, bool):
            regex.append("\d+")
        elif isinstance(numbered, int):
            regex.append(str(numbered))

        if isinstance(subkey, str):
            regex.append("-%s" % subkey)
        elif subkey is True:
            regex.append("-.+")

        if strict:
            regex.append("$")

        vals = (x for x in self.entity._attrs if re.match(''.join(regex), x.key))
        if value:
            vals = (x for x in vals if x.value == value)
            
        if not vals:
            return None
        return vals



    def attrKeys(self, *args, **kwargs):

        return (x.key for x in self.attrs(*args, **kwargs))

    def attrItems(self, *args, **kwargs):
        return ((x.key, x.value) for x in self.attrs(*args, **kwargs))

    def addAttr(self, key, value, numbered=None, subkey=None):
        """
        add a key/value to the list of attributes

        if num is True, append the next available int to the key name.
        if num is an int, append that int to the key name
        if subkey is specified append '_subkey' to the key name
         subkeys don't get numbered
        """

        keyname = self._buildKeyName(key, numbered, subkey)
        self.entity._attrs.append(Attribute(keyname, value))

    def delAttrs(self, *args, **kwargs):
        "delete attribute with the given key and value optionally value also"


        for i in self.attrs(*args, **kwargs):
            self.entity._attrs.remove(i)
            i.delete()

    def setAttr(self, key, valuelist):
        """
        replaces all items in the list matching the given key with values in
        valuelist
        """
        self._checkAttrName(key)
        self.delAttrs(key=key)
        for val in valuelist:
            self.addAttr(key, val)

    
    def hasAttr(self, strict=True, *args, **kwargs):
        "return True if this list has an attribute with the given key"

        for i in self.attrs(strict=strict, *args, **kwargs):
            return True

        return False
    

    
class PoolMixin:
    """
    mixin so Entities can interact with pools they are in
    """

    def mergedAttrs(self, *args, **kwargs):

        for pool in self.pools():
            pass

    
    def Xattrs(self, key=None, numbered=None, subkey=None, ignoreHidden=True,
              onlyLocal=False):

        all = AttributeListMixin.attrs(self, key, num, subkey, ignoreHidden)

        if not onlyLocal:
            for pool in self.pools():
                all.extend(pool.attrs(key, num, subkey, ignoreHidden,
                                      onlyLocal=onlyLocal))

            
        return all
    
    
    def Xpools(self):

        pools = [self.__class__(entity=x.value) for x in self.getAttr('_in', all=True, onlyLocal=True)]

        return pools


    def XremoveFromPools(self):
        "Remove this Entity from all pools"

        for pool in self.pools:
            pool.removeFromPool(self)

        

