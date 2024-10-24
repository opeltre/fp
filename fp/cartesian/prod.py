from fp.meta import Type, NFunctor, Functor
from typing import Callable
import fp.io as io


class Prod(Type, metaclass=Functor):

    src = Type
    tgt = Type

    arity = ...
    _kind_ = ..., ()

    """
    Product functor: typed subclasses of `tuple`.
    
    Example:
    --------
    .. code::

        >>> a, b = Str("abcd"), Int(8)
        >>> x = Prod(Str, Int)(a, b)
        >>> x
        (Str, Int) : ('abcd', 8)
        >>> @Hom(Int, Str)
        ... def bar(n): return n * "|"
        ...
        >>> Pf = Prod.fmap(Str.len, bar).show()
        (Str, Int) -> (Int, Str) : (len, bar)
        >>> Pf(x)
        (Int, Str) : (4, '||||||||')
    """

    class Object(tuple, metaclass=Type):
        """
        Product base type: `tuple` alias.
        """

        def __new__(P, *xs):
            if len(xs) != len(P._tail_):
                raise TypeError(f"Got {len(xs)} terms in product type {P.__name__}")
            xs = [io.cast(x, A) for A, x in zip(P._tail_, xs)]
            return super().__new__(P, xs)

        def __init__(prod, *xs): ...

        def __str__(self):
            return "(" + ", ".join(str(x) for x in self) + ")"

        def __repr__(self):
            return "(" + ", ".join(str(x) for x in self) + ")"

        @classmethod
        def proj(self, idx):
            @Type.Hom(self, self._tail_[idx])
            def p(*xs):
                return xs[idx]

            p.__name__ += f"[{idx}]"
            return p

        @classmethod
        def cast(P, xs):
            if not isinstance(xs, P):
                return P(*(io.cast(x, A) for A, x in zip(P._tail_, xs)))

    @classmethod
    def new(cls, *As):
        return super().new(*As)

    def __init__(P, *As): ...

    def __getitem__(P, i: int | slice):
        if isinstance(i, int):
            return P._tail_[i]
        return P.__class__(*P._tail_[i])

    def __len__(P):
        return len(P._tail_)

    @classmethod
    def fmap(cls, *fs: Callable) -> Callable:
        """
        Map a collection of functions to their joint action.

        Given maps `f : X -> A`, `g : Y -> B`, ... return the product map

            (f, g, ...) : (X, Y, ...) -> (A, B, ...)
        """
        src = cls(*(f.src for f in fs))
        tgt = cls(*(f.tgt for f in fs))

        @Type.Hom(src, tgt)
        def map_f(*xs):
            ys = tuple(f(x) for x, f in zip(xs, fs))
            return ys

        map_f.__name__ = cls._fmap_name_(*fs)
        return map_f

    @classmethod
    def _fmap_name_(cls, *fs):
        return "(" + ", ".join((f.__name__ for f in fs)) + ")"

    @classmethod
    def branch(cls, f: Callable, *fs: Callable) -> Callable:
        """
        Universal property of categorical products.

        Given a collection of arrows with the same source `X`,
        return an arrow from `X` to the product of targets.

            (X -> A, X -> B, ...) -> X -> (A, B, ...)

        The terminal arrow to `(A, B, ...)` has the input maps as
        projections.
        """
        src = f.src
        tgt = cls(*(fi.tgt for fi in (f, *fs)))

        @Type.Hom(src, tgt)
        def branch_f(x):
            """Map a souce type `X` to a product `(A, B, ...)`."""
            return (fi(x) for fi in (f, *fs))

        branch_f.__name__ = "branch " + cls._fmap_name_(f, *fs)
        return branch_f

    @classmethod
    def _get_name_(cls, *As):
        return "(" + ", ".join(A.__name__ for A in As) + ")"

    @classmethod
    def cast(cls, xs):
        if isinstance(xs, tuple):
            return cls(*xs)
        return io.cast(xs, cls)


""" Monoidal Unit """
Prod.Unit = Prod()
