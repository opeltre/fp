import pytest 
from typing import Any

import fp
from fp import Int, Str
from fp.meta import Type, Functor, Monad

class TestFunctor: 

    class F(Type, metaclass=Functor):
        """A writer functor F(A) = (str, A)"""

        class Object(tuple[str, Any]):
            ...

        @classmethod
        def fmap(cls, f):
            """Write f to string and act on carried value."""

            @Type.Hom(cls(f.src), cls(f.tgt))
            def map_f(sx): 
                s, x = sx
                return (s + f" | {f}", f(x))
            
            return map_f
    
    def test_type_subclass(self):
        assert issubclass(self.F, Type)

    def test_object_type(self): 
        FA = self.F(fp.Int)
        assert isinstance(FA, type) and isinstance(FA, Type)

    def test_object_init(self):
        FA = self.F(int)
        Fx = FA(("x0", 0))
        assert isinstance(Fx, FA) 

    def test_fmap_type(self):
        Flen = self.F.fmap(Str.len)
        assert Flen.src == self.F(Str)
        assert Flen.tgt == self.F(Int)

    def test_fmap_call(self):
        Fx = self.F(Str)(("x", "Hello world!"))
        Flen = self.F.fmap(Str.len)
        Fy = Flen(Fx) 
        assert Fy[1] == len(Fx[1])
        assert isinstance(Fy, Flen.tgt)
