from .type import Type, TypeClass
from .method import Method
from .functor import BifunctorClass, NFunctorClass
from .prod import Prod

from typing import Iterable

import fp.io as io


class ArrowClass(BifunctorClass):
    """
    Arrow type class. 

    A bifunctor instance `Arr` implements composition:

        Arr.compose: Arr(b, c) -> Arr(a, b) -> Arr(a, c)
    """
    @Method
    def compose(Arr):
        return (Arr('B', 'C'), Arr('A', 'B')), Arr('A', 'C')


class Arrow(metaclass=ArrowClass):
    
    @classmethod
    def new(cls, A, B):

        class Arrow_AB(Type):

            src = A
            tgt = B

        return Arrow_AB

    @classmethod
    def fmap(cls, phi):
        return lambda f: phi @ f

    @classmethod
    def cofmap(cls, psi):
        return lambda f: f @ psi

    @classmethod
    def compose(cls, phi, psi):
        return cls(psi.src, phi.tgt)

class HomClass(ArrowClass):
    """
    Morphism type class.

    An arrow instance `Hom` implements evaluation:

        Hom.eval: a -> Hom(a, b) -> b
    """

    @Method
    def eval(Hom):
        return ('A', Hom('A', 'B')), 'B'


class HomType(Type):

    src: type
    tgt: type
    arity: int

    def __init__(self, f: callable | Iterable[callable]):
        """
        Initialize from callable or pipe (iterable of callables).
        """
        if not callable(f):
            raise TypeError(f"Input is not callable.")
        self.call = f
        if "__name__" in dir(f) and f.__name__ != "<lambda>":
            self.__name__ = f.__name__
        else:
            self.__name__ = "\u03bb"

    def __call__(arrow, *xs):
        """
        Function application with type checks and curryfication.
        """
        f = arrow.call
        r = arrow.arity

        # --- Input and output types
        Src = arrow.source_type(arrow, xs)
        Tgt = arrow.target_type(arrow, xs)

        # --- Full application
        if len(xs) == arrow.arity:
            Tx = arrow.source_cast(Src, r, xs)
            y = f(Tx) if len(xs) == 1 else f(*Tx)
            Ty = arrow.target_cast(Tgt, y)
            return Ty

        # --- Curried section
        if len(xs) < arrow.arity:
            return arrow.curry(xs)

    def __matmul__(self, other):
        """Composition"""
        # arrow
        if "tgt" in dir(other):
            Arr = self._head
            if self.src == other.tgt:
                comp = Arr.compose(self, other)
                comp.__name__ = f"{self.__name__} . {other.__name__}"
                return comp
            raise TypeError(
                f"Uncomposable pair"
                + f"{(self.src, self.tgt)} @"
                + f"{(other.src, other.tgt)}"
            )
        # apply to input
        out = self(other)
        return out

    def curry(f, xs):
        """
        Curried function applied to n-ary input xs for n < arity.
        """
        if len(xs) < f.arity:
            ts = f.src._tail[-(f.arity - len(xs)) :]
            src = tuple(ts) if len(ts) > 1 else ts[0]

            @f._head(src, f.tgt)
            def curried(*ys):
                return f(*xs, *ys)

            curried.__name__ = f"{f.__name__} " + " ".join((str(x) for x in xs))
            return curried

        raise TypeError(
            f"Cannot curry {Arr.arity} function on " + f"{len(xs)}-ary input"
        )

    @staticmethod
    def source_type(arrow, xs):
        if "source_type" in dir(arrow._head):
            return arrow._head.source_type(arrow, xs)
        if len(xs) == arrow.arity:
            return arrow.src
        else:
            ts = arrow.src._tail[: len(xs)]
            return Prod(*ts)

    @staticmethod
    def source_cast(Src, r, xs):
        if r == 1 and isinstance(xs[0], Src):
            return xs[0]
        elif r > 1 and all(isinstance(x, S) for x, S in zip(xs, Src._tail)):
            return xs
        elif "cast" in dir(Src):
            return Src.cast(*xs)
        raise TypeError(f"Could not cast input")

    @staticmethod
    def target_type(arrow, xs):
        if "target_type" in dir(arrow._head):
            return arrow._head.target_type(arrow, xs)
        if len(xs) == arrow.arity:
            return arrow.tgt
        else:
            ts = arrow.src._tail[len(xs) :]
            return arrow._head(Prod(*ts), arrow.tgt)

    @staticmethod
    def target_cast(Tgt, y):
        if isinstance(y, Tgt):
            return y
        elif "cast" in dir(Tgt):
            return Tgt.cast(y)
        raise TypeError(f"Could not cast output")

    def __repr__(self):
        return self.__name__


class Hom(Arrow, metaclass=HomFunctor):
    
    instance = HomType

    @classmethod
    def new(cls, A, B):
        
        _src, _tgt, _arity = cls._parse_tail(A, B)

        class TAB(HomType):

            src = _src
            tgt = _tgt
            arity = _arity 

        return TAB
    
    def __init__(TAB, A, B):
        ...

    @classmethod
    def compose(cls, f, g):
        """Composition of functions"""
        return cls(g.src, f.tgt)(lambda *xs: f(g(*xs)))
    
    @classmethod
    def eval(cls, x, f):
        return f(x)

    @classmethod
    def name(cls, A, B):
        """Return __name__ attribute of arrow type."""
        def name_one(C, wrap_arr=True):
            if hasattr(C, '__name__'):
                if wrap_arr and hasattr(C, '_head') and hasattr(C._head, 'compose'):
                    return '(' + C.__name__ + ')'
                else:
                    return C.__name__
            else:
                return str(C)
        
        if isinstance(A, (tuple, list)):
            src = " -> ".join(name_one(C) for C in A)
            return src + " -> " + name_one(B)

        else:
            return name_one(A) + " -> " + name_one(B)
    
    @classmethod
    def _parse_tail(cls, A: type | Iterable[type], B: type):
        """Check that `A: type | Iterable[type] and B: type`."""
        if isinstance(A, type) and isinstance(B, type):
            _src, _tgt, _arity = (A, B, 1)
        elif "__iter__" in dir(A) and isinstance(B, type):
            As = Prod(*A)
            _src, _tgt, _arity = (As, B, len(As._tail))
        elif isinstance(B, type):
            raise TypeError(f"Source {A} is not a type nor an iterable of types")
        else:
            raise TypeError(f"Target {B} is not a type")
        return _src, _tgt, _arity
