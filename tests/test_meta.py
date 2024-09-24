import pytest
from typing import Any

import fp
from fp import Int, Str
from fp.meta import Type, Functor, Monad


class TestFunctor:

    class T(Type, metaclass=Functor):
        """A writer functor T(A) = (str, A)"""

        src = Type
        tgt = Type

        class Object(tuple[str, Any], Functor.TopType): ...

        @classmethod
        def fmap(cls, f):
            """Write f to string and act on carried value."""

            @Type.Hom(cls(f.src), cls(f.tgt))
            def map_f(sx):
                s, x = sx
                return (s + f" | {f}", f(x))

            return map_f

    def test_type_subclass(self):
        assert issubclass(self.T, Type)

    def test_object_type(self):
        FA = self.T(fp.Int)
        assert isinstance(FA, type) and isinstance(FA, Type)

    def test_object_init(self):
        FA = self.T(int)
        Fx = FA(("x0", 0))
        assert isinstance(Fx, FA)

    def test_fmap_type(self):
        Flen = self.T.fmap(Str.len)
        assert Flen.src == self.T(Str)
        assert Flen.tgt == self.T(Int)

    def test_fmap_call(self):
        Tx = self.T(Str)(("x", "Hello world!"))
        Tlen = self.T.fmap(Str.len)
        Ty = Tlen(Tx)
        assert Ty[1] == len(Tx[1])
        assert isinstance(Ty, Tlen.tgt)

    def test_bound_map(self):
        Tx = self.T(Str)(("x", "yo"))
        Ty = Tx.map(Str.len)
        assert Ty[1] == 2
        assert isinstance(Ty, self.T(Int))


class TestMonad(TestFunctor):

    class T(TestFunctor.T, metaclass=Monad):
        """A writer monad F(A) = (str, A)"""

        class Object(TestFunctor.T.Object, Monad.TopType): ...

        @classmethod
        def unit(cls, x):
            return cls(type(x))(("", x))

        @classmethod
        def bind(cls, mx, mf):
            MB = mf.tgt
            sx, x = mx
            sy, y = mf(x)
            return MB((sx + sy, y))

    def test_unit(self):
        mx = self.T.unit(Int(3))
        assert isinstance(mx, self.T(Int))

    def test_join(self):
        unit, x = self.T.unit, Int(4)
        mmx = unit(unit(x))
        mx = self.T.join(mmx)
        assert isinstance(mx, self.T(Int))
        assert mx == unit(x)

    def test_bind_bound(self):

        @Type.Hom(Int, self.T(Str))
        def bar(n):
            return ("bar", Str("|" * n))

        Tx = self.T(Int)(("foo", 6))
        Ty = Tx.bind(bar)
        sy, y = Ty
        assert sy == "foobar" and y == "||||||"
        assert isinstance(Ty, self.T(Str))
