import unittest

from fp.meta import Variable, Constructor, Arrow
from fp.instances import List, Int, Str


class TestVariable(unittest.TestCase):

    def test_variable(self):
        A = Variable("A")
        self.assertTrue(isinstance(A, type))
        self.assertTrue(A.__name__ == "A")
        result = A.match(Int)
        expect = {"A": Int}
        self.assertEqual(expect, result)

    ############
    # Requires update from TypeVar 4e552dec
    ############

    def test_match(self):
        T, F = Constructor("T"), Constructor("F")
        TAB = T(F("A"), "B")
        self.assertTrue(isinstance(TAB, Variable))
        # match
        result = TAB.match(T(F(Int), Str))["A"]
        self.assertEqual(Int, result)
        # no match
        result = TAB.match(T(Int, Str))
        self.assertEqual(result, None)
        # no match
        result = TAB.match(Arrow(List(Int), Int))
        self.assertEqual(result, None)

    def test_substitute(self):
        A = Arrow("a", "a")
        result = A.substitute({"a": Int})
        expect = Arrow(Int, Int)
        self.assertEqual(expect, result)
        B = Arrow(List("b"), "c")
        result = B.substitute({"b": Str, "c": Int})
        expect = Arrow(List(Str), Int)
        self.assertEqual(expect, result)
