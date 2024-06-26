import unittest

from fp import Str, Int, Wrap, Hom


class TestWrap(unittest.TestCase):

    def test_wrap(self):
        x = Wrap(Str)("salut")
        result = isinstance(x.data, Str)
        self.assertTrue(result)
        y = Wrap(Int)(5)
        result = isinstance(y.data, Int)
        self.assertTrue(result)

    def test_fmap(self):
        x = Wrap(Str)("yo")
        f = Hom(Str, Int)(len)
        Wf = Wrap.fmap(f)
        result = Wf(x)
        expect = Wrap(Int)(2)
        self.assertEqual(expect, result)
