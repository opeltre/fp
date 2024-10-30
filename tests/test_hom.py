import pytest

from fp.meta import Type
from fp.cartesian import Hom

# we need at least 2 types
A = Type("A", (int,), {})
B = Type("B", (str,), {})

HomObject = Hom.Object


class TestHomObject:

    class HomAB(HomObject):
        src = int
        tgt = str
        arity = 1

    class HomBA(HomObject):
        src = str
        tgt = int
        arity = 1

    class HomBAB(HomObject):
        src = Type.Prod(str, int)
        tgt = str
        arity = 2

    foo = HomBA(lambda s: len(s))
    bar = HomAB(lambda n: "|" * n)
    foobar = HomBAB(lambda s, n: s * n)

    def test_eq(self):
        assert self.bar == self.bar
        assert self.foo != self.bar

    def test_hash(self):
        d = {self.bar: "bar", self.foo: "foo"}
        assert len(d) == 2

    ### application ###

    def test_call(self):
        foo_abc = self.foo("abc")
        assert foo_abc == 3
        bar_4 = self.bar(4)
        assert bar_4 == "||||"

    def test_lshift(self):
        foo_x = self.foo << "x"
        assert foo_x == 1

    ### composition ###

    @pytest.mark.xfail
    def test_matmul_fail(self):
        self.foo @ self.foo

    def test_matmul(self):
        self.foo._head_ = Hom
        self.bar._head_ = Hom
        foo_bar = self.foo @ self.bar
        bar_foo = self.bar @ self.foo
        assert (foo_bar.src, foo_bar.tgt) == (self.bar.src, self.foo.tgt)
        assert (bar_foo.src, bar_foo.tgt) == (self.foo.src, self.bar.tgt)

    def test_matmul_eval(self):
        self.foo._head_ = Hom
        self.bar._head_ = Hom
        foo_bar = self.foo @ self.bar
        bar_foo = self.bar @ self.foo
        assert foo_bar(4) == 4
        assert bar_foo("toto") == "||||"

    ### source_type ###

    def test_source_type_unary(self):
        Tx, match_x = HomObject.source_type(self.foo, ("abc",))
        Ty, match_y = HomObject.source_type(self.bar, (3,))
        assert Tx is str and match_x is True
        assert Ty is int and match_y is True

    def test_source_type_binary(self):
        Tx, match = HomObject.source_type(self.foobar, ("abc", 3))
        assert match is True
        assert Tx == Type.Prod(str, int)

    def test_source_type_partial(self):
        Tx, match = HomObject.source_type(self.foobar, ("abc",))
        assert match is True
        assert Tx == Type.Prod(
            str,
        )

    ### target_type ###

    def test_target_type_unary(self):
        Ty = HomObject.target_type(self.foo, ("abc",))
        assert Ty is int

    def test_target_type_binary(self):
        Ty = HomObject.target_type(self.foobar, ("abc", 2))
        assert Ty is str

    def test_target_type_partial(self):
        # called by curryfication
        self.foobar._head_ = Hom
        Ty = HomObject.target_type(self.foobar, ("abc",))
        assert Ty.arity == 1
        assert (Ty.src, Ty.tgt) == (Type.Prod(int), str)


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

    def test_empty_call(self):
        f = Hom((), int)(lambda: 1)
        assert f() == 1

    def test_matmul_call(self):
        foobar = self.foo @ self.bar
        barfoo = self.bar @ self.foo
        assert barfoo(B("cha")) == B("|||")
        assert foobar(A(32)) == A(32)

    def test_binary_signature(self):

        @Hom((A, A), A)
        def power(x, y):
            return x**y

        assert power.src is Type.Prod(A, A)
        assert power.tgt is A

    def test_binary_call_untyped(self):
        add = Hom((A, A), A)(int.__add__)
        assert add(4, 1) == 5

    def test_binary_call_typed(self):
        add = Hom((A, A), A)(int.__add__)
        x_y = add.src(2, 3)
        assert add(x_y) == 5

    def test_partial(self):
        power = Hom((A, A), A)(lambda x, y: x**y)
        pow2 = power(2)
        assert (pow2.src, pow2.tgt) == (A, A)
        assert pow2(6) == power(2, 6)

    def test_prod_in_pipe(self):
        add = Hom((A, A), A)(lambda x, y: x + y)
        eucdiv = Hom((A, A), Type.Prod(A, A))(divmod)
        assert add.arity == 2 and eucdiv.arity == 2
        assert len(eucdiv(12, 5)) == 2
        assert (add @ eucdiv).arity == 2
        assert (add @ eucdiv)(12, 5) == A(4)

    def test_prod_target(self):
        f = Hom((int, int), (int, int))(divmod)
        assert f.tgt is Type.Prod(int, int)
        assert f(7, 2) == (3, 1)
