import pytest

from fp.meta import Type
from fp.cartesian import Hom

# we need at least 2 types
A = Type("A", (int,), {})
B = Type("B", (str,), {})

class TestHom:
    
    foo = Hom(B, A)(lambda y: len(y))
    bar = Hom(A, B)(lambda x: "|" * x)

    def test_signature(self):
        foo, bar = self.foo, self.bar
        result = (bar.src, bar.tgt, foo.src, foo.tgt)
        expect = (A, B, B, A)
        assert expect == result

    def test_matmul_signature(self):
        foobar = self.foo @ self.bar
        barfoo = self.bar @ self.foo
        result = (foobar.src, foobar.tgt, barfoo.src, barfoo.tgt)
        expect = (A, A, B, B)
        assert expect == result

    def test_call(self):
        x = A(18)
        y = B("Eilenberg Mac-Lane")
        assert x == self.foo(y)

    def test_call_cast(self):
        assert self.bar(4) == B("||||")

    def test_matmul_call(self):
        foobar = self.foo @ self.bar
        barfoo = self.bar @ self.foo
        assert barfoo(B("cha")) == B("|||")
        assert foobar(A(32)) == A(32)
    
    def test_nary_signature(self):

        @Hom((A, A), A)
        def power(x, y):
            return x ** y

        assert power.src is Type.Prod(A, A)
        assert power.tgt is A

    def test_partial(self): 
        power = Hom((A, A), A)(
            lambda x, y: x ** y
        )
        pow2 = power(2)
        assert (pow2.src, pow2.tgt) == (A, A)
        assert pow2(6) == power(2, 6)
