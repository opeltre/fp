import unittest

from fp.meta import TypeVar, Arrow
from fp.instances import List, Int, Str

class TestTypeVar(unittest.TestCase):

    def test_typevar(self):
        A = TypeVar('A')
        self.assertTrue(isinstance(A, type))
        self.assertTrue(A.__name__ == 'A')
        result = A.match(Int)
        expect = {'A' : Int}
        self.assertEqual(expect, result)

    def test_functorvar(self):
        TAB = Arrow(List('A'), Str)
        self.assertTrue(isinstance(TAB, TypeVar))
        # match
        result = TAB.match(Arrow(List(Int), Str))
        expect = {'A': Int}
        self.assertEqual(expect, result)
        # no match
        result = TAB.match(Arrow(Int, Str))
        self.assertEqual(result, None)
        # no match
        result = TAB.match(Arrow(List(Int), Int))
        self.assertEqual(result, None)
