import unittest as test

from fp import List, Hom, Str, Int


class TestList(test.TestCase):

    def test_type_constructor(self):
        self.assertTrue(isinstance(List(Str), type))

    def test_init(self):
        x = List(Str)(["peppers", "tomatoes", "zukinis"])
        self.assertTrue(isinstance(x, List(Str)))

    def test_fmap(self):
        foo = Hom(Str, Int)(len)
        Lfoo = List.fmap(foo)
        self.assertTrue(isinstance(Lfoo, Hom(List(Str), List(Int))))
        x = ["apples", "lemons", "peaches"]
        y = Lfoo(x)
        self.assertTrue(isinstance(Lfoo(x), List(Int)))
