from __future__ import annotations

from fp.meta import Type, Monad 
from .num import Int, Monoid

import fp.io as io

class List(Monoid, metaclass=Monad):

    src = Type
    tgt = Type
    
    class Object(list, Monad._instance_):
         
        def __init__(self, xs):
            A = self._tail_[0]
            try:
                ys = (io.cast(x, A) for x in xs)
                super().__init__(ys)
            except Exception as e:
                raise io.TypeError("input", xs, self.__class__)

        def __repr__(self):
            return "[" + ", ".join([str(x) for x in self]) + "]"

        def __str__(self):
            return "[" + ", ".join([str(x) for x in self]) + "]"
    
        @classmethod
        def cast(cls, xs):
            if hasattr(xs, '__iter__'):
                return cls(xs)
            print(type(xs))
            raise TypeError()


    @classmethod
    def new(cls, A):
        return Monoid.__new__(cls, 'List A', (cls.Object,), {})
    
    @classmethod
    def fmap(cls, f: Hom("A", "B")) -> Hom(cls("A"), cls("B")):
        """
        Map a function on lists.
        """
        @Type.Hom(cls(f.src), cls(f.tgt))
        def mapf(xs):
            return [f(x) for x in xs]

        mapf.__name__ = f"map {f.__name__}"
        return mapf
    
    @classmethod
    def join(cls, xx: cls(cls("A"))) -> cls("A"):
        """
        Flatten a list of lists.
        """
        A = xx._tail_[0]._tail_[0]
        return cls(A)(sum((x for  x in xx), []))
    
    @classmethod
    def unit(cls, a):
        """
        Singleton list.
        """
        return cls(type(a))([a])
    

List.range = Type.Hom(Int, List(Int))(lambda n: range(n))
List.range.__name__ = "range"
