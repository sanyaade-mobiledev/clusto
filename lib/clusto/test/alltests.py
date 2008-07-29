
import unittest
import sys

import clusto.test


def runtests(tests=None):

    if not tests:
        tests = ('clusto.test.base', 'clusto.test.drivers',)

    suite = unittest.defaultTestLoader.loadTestsFromNames(tests)
    runner = unittest.TextTestRunner()
    runner.run(suite)




if __name__ == '__main__':
    runtests(sys.argv[1:])
