import unittest

from fp import Tens, Linear, Otimes

E, F = Tens([3]), Tens([2, 3])
A, B = Tens([4]), Tens([6])

class TestOtimes(unittest.TestCase):

    def test_obj(self):
        result = Otimes(E, F)
        expect = Tens([3, 2, 3])
        self.assertEqual(expect, result)

    def test_fmap_dense(self):
        f = Linear(E, F).randn()
        g = Linear(A, B).randn()
        fg = Otimes.fmap(f, g)
        Tfg = type(fg)
        self.assertTrue(fg.src, Tens([3, 4]))
        self.assertTrue(fg.tgt, Tens([2, 3, 6]))