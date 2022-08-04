import unittest as test

from fp import List, Arrow, Str, Int

class TestList(test.TestCase):

    def test_type_constructor(self):
        self.assertTrue(isinstance(List(Str), type))

    def test_init(self):
        x = List(Str)(["peppers", "tomatoes", "zukinis"])
        self.assertTrue(isinstance(x, List(Str)))

    def test_fmap(self):
        foo = Arrow(Str, Int)(len)
        Lfoo = List.fmap(foo)
        self.assertTrue(isinstance(Lfoo, Arrow(List(Str), List(Int))))
        x = ["apples", "lemons", "peaches"]
        y = Lfoo(x)
        self.assertTrue(isinstance(Lfoo(x), List(Int)))
