
import unittest

from clusto.schema import AttributeDict
import testbase

class TestAttributeDict(testbase.ClustoTestBase):

    def testAttrDictReturnValue(self):

        a = AttributeDict()
        a['foo'] = 1

        self.assert_(a['foo'] == [1])

    def testAttrDictInit(self):

        a = AttributeDict({'foo':1,
                           'bar':2})

        self.assert_(a['foo'] == [1])
        

    def testAttrDictToList(self):

        a = AttributeDict()

        a['a'] = [1,2]
        a['b'] = 3

        expected = [('a', 1), ('a', 2), ('b',3)]
        expected.sort()


        result = a.items()
        result.sort()

        self.assert_(expected == result)
