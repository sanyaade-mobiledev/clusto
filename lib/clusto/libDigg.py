import UserDict
import time

def fopen (filename,mode):
    """tries to open a file and returns a file handle on success or 1 on error"""

    try:
        f = open (filename,mode)
    except:
        print "file does not exist"
        return 1
    else:
        return f


def tempFile():

    # for the moment, don't use this more than once a second
    t = time.time()
    name = "/tmp/temp--%s" % t
    return (name)

# cool, but keys must be integers
# see
# http://the.taoofmac.com/static/grimoire.html#contents_item_5.5
class MultipleDict(UserDict.UserDict):
    def __setitem__(self, key, item):
        if self.data.has_key( key ):
            self.data[key].append( item )
        else:
            self.data[key] = [item]

