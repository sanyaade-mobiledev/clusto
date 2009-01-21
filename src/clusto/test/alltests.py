
if __name__ == '__main__':

    import os
    import sys


    sys.path.append(os.path.realpath('.'))


import unittest
import clusto.test


def gettests(tests=None):
    if not tests:
        tests = ('clusto.test.base', 'clusto.test.drivers',
                 'clusto.test.usage',)

    suite = unittest.defaultTestLoader.loadTestsFromNames(tests)

    return suite


def runtests(tests=None):

    suite = gettests(tests)
    runner = unittest.TextTestRunner()    
    runner.run(suite)




if __name__ == '__main__':

    runtests(sys.argv[1:])
