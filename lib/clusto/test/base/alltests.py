
from clusto.test import testbase
import unittest

def suite():
    modues_to_test = (
        'base.Thing',
        )

    alltests = unittest.TestSuite()

    for name in modues_to_test:
        
