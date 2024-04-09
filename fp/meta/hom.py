from .functor import BifunctorClass, NFunctorClass
from .type import Type

import fp.io as io

from .arrow import ArrowClass

from typing import Literal


class Prod(metaclass=NFunctorClass):
    """
    Product functor.
    """

    @classmethod
    def new(cls, *As: tuple[type, ...]) -> type:
        """
        Product type.
        """

        class Prod_As(tuple):

            def __new__(P, *xs):
                if len(xs) != len(P._tail):
                    raise TypeError(f"Got {len(xs)} terms in product type {P.__name__}")
                xs = [io.cast(x, A) for A, x in zip(P._tail, xs)]
                return super().__new__(P, xs)

            def __init__(prod, *xs): ...

            def __repr__(self):
                return "(" + ", ".join(str(x) for x in self) + ")"

            @classmethod
            def cast(P, xs):
                if not isinstance(xs, P):
                    return P(*(A.cast(x) for A, x in zip(P._tail, xs)))

        return Prod_As

    @classmethod
    def fmap(cls, *fs):

        src = cls((f.src for f in fs))
        tgt = cls((f.tgt for f in fs))

        @Hom(src, tgt)
        def map_f(*xs):
            return tgt(*(f(x) for x, f in zip(xs, fs)))

        map_f.__name__ = "(" + ", ".join((f.__name__ for f in fs)) + ")"
        return map_f

    @classmethod
    def name(cls, *As):
        return "(" + ", ".join(A.__name__ for A in As) + ")"


class Hom(metaclass=ArrowClass):

    @classmethod
    def new(cls, A, B):

        class Hom_AB:
            src, tgt = A, B

            def __new__(cls, f):
                if isinstance(f, Hom):
                    return f
                self = super().__new__(cls)
                self.call = f
                return self

            def __call__(self, *xs, **ks):
                # function call
                if callable(self.call):
                    y = self.call(*xs, **ks)
                # pipe call
                elif hasattr(self.call, "__iter__"):
                    f, *fs = self.call
                    y = f(*xs, **ks)
                    for f in fs:
                        y = f(y)
                    return y
                return y if self.tgt is None else self.tgt.cast(y)

            def __matmul__(self, other):
                expand = lambda f: [f] if callable(f) else f
                cls(other.src, self.tgt)([*other.call, *self.call])

        return Hom_AB

    @classmethod
    def fmap(cls, f: Literal["B -> C"]) -> Literal["Hom('A', 'B') -> Hom('A', 'C')"]:
        """Pushforward functor."""

        def push_f(phi):
            return f @ phi

        return push_f


Type.Hom = Hom
