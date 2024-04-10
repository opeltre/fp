from .functor import NFunctorClass
from .type import TypeClass

import fp.io as io

class ProdType(tuple, metaclass=TypeClass):
    """
    Base class for product instances (x1, ..., xn).
    """

    def __new__(cls, *xs):
        if len(xs) != len(cls._tail):
            raise TypeError(
                f"Invalid number of terms {len(xs)} "
                + f"for {len(cls._tail)}-ary product."
            )
        elems = [io.cast(x, A) for A, x in zip(cls._tail, xs)]
        return super().__new__(cls, elems)

    def __init__(self, *xs):
        ...

    def __repr__(self):
        return "(" + ", ".join([str(x) for x in self]) + ")"

    @classmethod
    def cast(cls, *xs):
        ys = [io.cast(x, A) for A, x in zip(cls._tail, xs)]
        return cls(*ys)


class Prod(metaclass=NFunctorClass):
    """
    Cartesian product functor.
    """
    
    @classmethod
    def new(cls, *As):

        class Prod_As(ProdType):

            _head = cls
            _tail = As
        
        return Prod_As

    def __init__(TA, *As):
        ...

    @classmethod
    def fmap(cls, *fs):

        src = cls((f.src for f in fs))
        tgt = cls((f.tgt for f in fs))

        @Arrow(src, tgt)
        def map_f(*xs):
            return tgt(*(f(x) for x, f in zip(xs, fs)))

        map_f.__name__ = "(" + ", ".join((f.__name__ for f in fs)) + ")"
        return map_f

    @classmethod
    def name(cls, *As):
        names = [A.__name__ for A in As]
        return f"({', '.join(names)})"
