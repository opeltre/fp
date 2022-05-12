import unittest

from fp.instances import Str, Int, Wrap
from fp.meta      import Arrow

class TestWrap (unittest.TestCase):

    def test_wrap(self):
        x = Wrap(Str)("salut")
        result = isinstance(x.data, Str)
        self.assertTrue(result)
        y = Wrap(Int)(5)
        result = isinstance(y.data, Int)
        self.assertTrue(result)

    def test_fmap(self):
        x = Wrap(Str)("yo")
        f = Arrow(Str, Int)(len)
        Wf = Wrap.fmap(f)
        result = Wf(x)
        expect = Wrap(Int)(2)
        self.assertEqual(expect, result)