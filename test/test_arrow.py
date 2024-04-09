import unittest

from fp.meta import TypeClass, Arrow

A = TypeClass("A", (int,), {})
B = TypeClass("B", (str,), {})

foo = Arrow(B, A)(lambda y: len(y))
bar = Arrow(A, B)(lambda x: "|" * x)


@Arrow((A, A), A)
def power(x, y):
    return x**y


class TestArrow(unittest.TestCase):

    def test_src_tgt(self):
        result = (bar.src, bar.tgt, foo.src, foo.tgt)
        expect = (A, B, B, A)
        self.assertEqual(expect, result)

    def test_matmul(self):
        foobar = foo @ bar
        barfoo = bar @ foo
        result = (foobar.src, foobar.tgt, barfoo.src, barfoo.tgt)
        expect = (A, A, B, B)
        self.assertEqual(expect, result)

    def test_call(self):
        x = A(18)
        y = B("Eilenberg Mac-Lane")
        self.assertEqual(x, foo(y))
        z = bar(18)
        self.assertTrue(isinstance(z, B))
        self.assertEqual(z, (bar @ foo)(y))

    def test_curry(self):
        """Test curryfication"""
        pow2 = power(2)
        result = type(power)
        expect = Arrow(A, A)
        self.assertTrue(expect, result)
        self.assertEqual(pow2(3), A(8))

    def test_untyped(self):
        add = Arrow((int, int), int)(int.__add__)
        self.assertEqual(add(2, 3), 5)


# --- Abstract arrows


class Order(Arrow):

    def __new__(cls, A, B):

        TAB = super().__new__(cls, A, B)
        TAB.arity = 0

        def _init_(self, data=None):
            self.call = lambda: None
            self.data = data

        def _new_(Tab, data=None):
            return super().__new__(Tab, lambda: None)

        TAB.__init__ = _init_
        TAB.__new__ = _new_

        return TAB

    def __init__(self, A, B):
        pass

    @classmethod
    def name(cls, *As):
        return " > ".join(str(A) for A in As)


class TestAbstractArrow(unittest.TestCase):

    def test_abstract_arrow(self):
        ab = Order("a", "b")
