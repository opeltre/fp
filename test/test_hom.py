import unittest

from fp.meta import TypeClass, Hom

A = TypeClass("A", (int,), {})
B = TypeClass("B", (str,), {})

foo = Hom(B, A)(lambda y: len(y))
bar = Hom(A, B)(lambda x: "|" * x)


@Hom((A, A), A)
def power(x, y):
    return x**y


class TestHom(unittest.TestCase):

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
        expect = Hom(A, A)
        self.assertTrue(expect, result)
        self.assertEqual(pow2(3), A(8))

    def test_untyped(self):
        add = Hom((int, int), int)(int.__add__)
        self.assertEqual(add(2, 3), 5)
