
import testbase
import unittest
import sys


tests = sys.argv[1:]

if not tests:
    tests = ('base', 'drivers',)


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromNames(tests)
    runner = unittest.TextTestRunner()
    runner.run(suite)
