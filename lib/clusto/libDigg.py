import UserDict

def fopen (filename,mode):
    """tries to open a file and returns a file handle on success or 1 on error"""

    try:
        f = open (filename,mode)
    except:
        print "file does not exist"
        return 1
    else:
        return f

# cool, but keys must be integers
# see
# http://the.taoofmac.com/static/grimoire.html#contents_item_5.5
class MultipleDict(UserDict.UserDict):
    def __setitem__(self, key, item):
        if self.data.has_key( key ):
            self.data[key].append( item )
        else:
            self.data[key] = [item]
