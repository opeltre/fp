import unittest

from fp import Int, Float, Bool
from fp.meta import Hom


class TestNum(unittest.TestCase):

    def test_add(self):
        # --- type
        result = type(Int.add)
        expect = Hom((Int, Int), Int)
        self.assertEqual(expect, result)
        # --- action
        self.assertTrue(2 + 3 == Int.add(2, 3))
        self.assertTrue(2 + 3 == Int.add(2)(3))
        self.assertTrue(2 + 3 == Int(2) + Int(3))

    def test_mul(self):
        # --- type
        result = type(Float.mul(2.0))
        expect = Hom(Float, Float)
        self.assertEqual(expect, result)
        # --- action
        self.assertTrue(6.0 == Float.mul(2, 3))
        self.assertTrue(6.0 == Float.mul(2)(3))
        self.assertTrue(6.0 == Float(2) * Float(3))

    def test_eq(self):
        result = type(Int.eq)
        expect = Hom((Int, Int), Bool)
        self.assertTrue(expect, result)
        self.assertTrue(Int(1) == Int(1))
