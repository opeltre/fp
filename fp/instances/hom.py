from __future__ import annotations
from .arrow import Arrow
from fp.meta import Type, HomFunctor, ArrowFunctor
from typing import Iterable, Callable

import fp.io as io

from typing import Literal


class HomInstance(Arrow._top_):
    """
    Base class for Hom(A, B) types.
    """

    src: Type
    tgt: Type
    arity: int
     
    def __init__(self, pipe: Callable | tuple[Callable]): 
        # wrap callables in the monoidal tuple type
        if isinstance(pipe, tuple):
            self._pipe = pipe
        elif callable(pipe) and self.arity == 1:
            self._pipe = (pipe,)
        elif callable(pipe) and not isinstance(type(pipe), Type.Hom):
            self._pipe = (lambda xs: pipe(*xs),)
        # set __name__  
        if callable(pipe):
            self.__name__ = (pipe.__name__ if pipe.__name__ != "<lambda>" else "λ")
    
    def __call__(self, *xs) -> tgt:
        
        def pipe(x):
            for f in self._pipe:
                x = f(x)
            return io.cast(x, self.tgt)

        # --- Input and output types
        Src = self.source_type(self, xs)
        Tgt = self.target_type(self, xs)

        # --- Full application
        if len(xs) == self.arity:
            Tx = self.source_cast(Src, self.arity, xs)
            y = pipe(Tx) if len(xs) == 1 else pipe(Tx)
            Ty = self.target_cast(Tgt, y)
            return Ty

        # --- Curried section
        if len(xs) < self.arity:
            return self._head_.curry(self, xs)
        
        else:
            raise io.TypeError("input", xs, self.src)

    def __lshift__(self, x:src) -> tgt:
        return self(x)
    
    def __rshift__(self, other):
        return self._head_.compose(self, other)

    def __repr__(self):
        if hasattr(self, '__name__'):
            return self.__name__
        name_one = lambda f: f.__name__ if f.__name__ != '<lambda>' else "λ"
        if len(self._pipe) < 4:
            return ' . '.join(name_one(f) for f in self._pipe[::-1])
        else:
            tail, head = self._pipe[0], self._pipe[-1]
            return name_one(head) + ' . (...) . ' + name_one(tail)

    @staticmethod
    def source_type(arrow, xs):
        if "source_type" in dir(arrow._head_):
            return arrow._head_.source_type(arrow, xs)
        if len(xs) == arrow.arity:
            return arrow.src
        else:
            ts = arrow.src._tail_[: len(xs)]
            return Type.Prod(*ts)

    @staticmethod
    def source_cast(Src, r, xs):
        if r == 1 and isinstance(xs[0], Src):
            return xs[0]
        elif r == 1: 
            return io.cast(xs[0], Src)
        elif r > 1 and all(isinstance(x, S) for x, S in zip(xs, Src._tail_)):
            return xs
        else:
            return io.cast(xs, Src)

    @staticmethod
    def target_type(arrow, xs):
        if "target_type" in dir(arrow._head_):
            return arrow._head_.target_type(arrow, xs)
        if len(xs) == arrow.arity:
            return arrow.tgt
        else:
            ts = arrow.src._tail_[len(xs) :]
            return arrow._head_(Type.Prod(*ts), arrow.tgt)

    @staticmethod
    def target_cast(Tgt, y):
        if isinstance(y, Tgt):
            return y
        elif "cast" in dir(Tgt):
            return Tgt.cast(y)
        raise TypeError(f"Could not cast output")


class Hom(Arrow, metaclass=HomFunctor):
    """
    Hom Functor.

    The type `Hom(A, B) = A -> B` describes callables with input in `A` 
    and output in `B`.
    """
    
    _top_ = HomInstance
    
    src = Type
    tgt = Type
    
    @classmethod
    def new(cls, A, B):
        TAB = super().new(A, B)
        # parse source type
        src, tgt, arity = cls._parse_input_(A, B)
        TAB.src = src
        TAB.tgt = tgt
        TAB.arity = arity
        return TAB

    def __init__(TAB, A, B):
        ...

    @classmethod
    def compose(cls, f, *fs):
        """
        Pipe a collection of functions. 

        The usual composition of two functions `f @ g` is 
        obtained as `Hom.compose(g, f)`. 
        Applied on an input `x`, this returned pipe satisfies:

        .. code::
            
            >>> Hom.compose(f, *fs)(x) == Hom.compose(*fs)(f(x))
            True

        Note:
        -----
        Composition is made associative by storing the sequence 
        of functions in a flat tuple, instead of stacking function
        closures. 
        """
        src = f.src
        tgt = (fs[-1] if len(fs) else f).tgt
        pipe = sum((list(fi._pipe) for fi in (f, *fs)), [])
        return cls(src, tgt)(tuple(pipe))

    @classmethod
    def eval(cls, x, f):
        """
        Evaluate `f` on input `x`.
        """
        return f(x)
    
    @classmethod
    def curry(cls, f, xs):
        """
        Curried function applied to n-ary input `xs` for n < arity.

        Example:
        --------

        .. code::

            >>> Int.add
            Int -> Int -> Int: add
            >>> Int.add(2, 3)
            Int: 5
            >>> Int.add(2):
            Int -> Int: add 2
            >>> Int.add(2)(3) 
            Int: 3
        """
        if len(xs) < f.arity:
            ts = f.src._tail_[-(f.arity - len(xs)) :]
            src = tuple(ts) if len(ts) > 1 else ts[0]

            @cls(src, f.tgt)
            def curried(*ys):
                return f(*xs, *ys)

            curried.__name__ = f"{f.__name__} " + " ".join((str(x) for x in xs))
            return curried

        raise TypeError(
            f"Cannot curry {Arr.arity} function on " + f"{len(xs)}-ary input"
        )

    @classmethod
    def _get_name_(cls, A, B):
        
        def name_one(T):
            if hasattr(T, '_head_') and isinstance(T._head_, ArrowFunctor):
                return "(" + T.__name__ + ")"
            elif hasattr(T, '__name__'):
                return T.__name__
            else:
                return str(T)

        if isinstance(A, tuple):
            return ' -> '.join(name_one(T) for T in A) + ' -> ' + name_one(B)
        else:
            return name_one(A) + ' -> ' + name_one(B)
    
    @classmethod
    def _parse_input_(cls, A, B):
        """
        Parse N-ary source types.
        """
        tgt = B
        if isinstance(A, type):
            # A -> B
            src, arity = A, 1
        elif isinstance(A, tuple):
            # (A1, ..., An) -> B
            src, arity = Type.Prod(*A), len(A)
        else:
            raise io.TypeError("source", A, Type | Iterable[Type])
        return src, tgt, arity
        

Type.Hom = Hom
