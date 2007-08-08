
import testbase
import unittest
import sys


tests = ('base',
         'drivers',)


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromNames(tests)
    runner = unittest.TextTestRunner()
    runner.run(suite)
