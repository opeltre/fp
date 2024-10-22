from __future__ import annotations

import functools

import types
from typing import Iterable, Callable, Literal

from fp import io
from fp.meta import Type, Var, HomFunctor, ArrowFunctor
from .arrow import Arrow


class HomObject(Arrow.Object):
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
            self.__name__ = pipe.__name__ if pipe.__name__ != "<lambda>" else "λ"

    def __call__(self, *xs) -> tgt:

        def pipe(x):
            for f in self._pipe:
                x = f(x)
            return x

        # --- Input and output types
        Src, match = self.source_type(self, xs)
        Tgt = self.target_type(self, xs, match)

        # --- Full application
        if (
            len(xs) == self.arity
            or (len(xs) == 1 and isinstance(xs[0], self.src))
            or (self.arity == 0 and len(xs) == 1)
        ):
            Tx = self.source_cast(Src, self.arity, xs)
            y = pipe(Tx)
            Ty = self.target_cast(Tgt, y)
            return Ty

        # --- Partial section
        if len(xs) < self.arity:
            return self._head_.partial(self, *xs)

        if self.arity == 0 and len(xs) == 1:
            x = xs[0]
            if x == Type.Unit() or x is None:
                return self()

        print(self.arity, len(xs))
        raise io.TypeError("input", xs, self.src)

    def __lshift__(self, x: src) -> tgt:
        return self(x)

    def __rshift__(self, other):
        return self._head_.compose(self, other)

    def __str__(self):
        if hasattr(self, "__name__"):
            return self.__name__
        return "λ"

    def __repr__(self):
        if hasattr(self, "__name__"):
            return self.__name__
        name_one = lambda f: f.__name__ if f.__name__ != "<lambda>" else "λ"
        if len(self._pipe) < 4:
            return " . ".join(name_one(f) for f in self._pipe[::-1])
        else:
            tail, head = self._pipe[0], self._pipe[-1]
            return name_one(head) + " . (...) . " + name_one(tail)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self._pipe == other._pipe

    def __hash__(self):
        return hash(self._pipe)

    @staticmethod
    def source_type(arrow, xs) -> tuple[type, bool | dict]:
        """Infer input type for downstream cast."""
        Prod = Type.Prod
        if "source_type" in dir(arrow._head_):
            # TODO: is this necessary?
            Src = arrow._head_.source_type(arrow, xs)

        elif len(xs) == arrow.arity:
            # n-ary call on n-fold input
            Src = arrow.src
        elif len(xs) == 1 and isinstance(xs[0], arrow.src):
            # n-ary call on Prod instance
            Src = arrow.src
        elif len(xs) <= arrow.arity:
            # partial call
            ts = arrow.src._tail_[: len(xs)]
            Src = Type.Prod(*ts)
        else:
            raise ValueError(
                f"too many arguments for {arrow.src} -> {arrow.tgt} on {xs}"
            )

        if not isinstance(Src, Var):
            # concrete type, True
            return Src, True
        else:
            # parametric type, match: dict
            Tx = Type.Prod(type(x) for x in xs) if len(xs) > 1 else type(xs[0])
            return Src, Src.match(Tx)

    @staticmethod
    def source_cast(Src, r, xs):
        """Cast input(s) to Src type."""
        if r == 1 and isinstance(xs[0], Src):
            # unary call (typed)
            return xs[0]
        if r == 1:
            # unary call (untyped)
            return io.cast(xs[0], Src) if not isinstance(Src, Var) else xs[0]

        if r > 1 and len(xs) == 1 and isinstance(xs[0], Src):
            # n-ary call (on single Prod instance)
            return xs[0]
        if r > 1 and all(isinstance(x, S) for x, S in zip(xs, Src._tail_)):
            # n-ary call (on n typed inputs)
            return xs

        if r == 0 and (len(xs) == 0 or xs[0] == Type.Unit() or xs[0] is None):
            # constant
            return Type.Unit()

        else:
            return io.cast(xs, Src) if not isinstance(Src, Var) else xs

    @staticmethod
    def target_type(arrow, xs: tuple, match=True) -> Type:
        """
        Target type inference.
        """

        def subst(ty):
            return ty.substitute(match) if isinstance(ty, Var) else ty

        if "target_type" in dir(arrow._head_):
            return arrow._head_.target_type(arrow, xs)
        if len(xs) == arrow.arity or (len(xs) == 1 and isinstance(xs[0], arrow.src)):
            # full application type
            if match is True or not isinstance(arrow.tgt, Var):
                # concrete type
                return arrow.tgt
            elif match is not None:
                # substitute type variables
                return arrow.tgt.substitute(match)
        else:
            # curried type
            As = tuple(subst(A) for A in arrow.src._tail_[len(xs) :])
            return arrow._head_(Type.Prod(*As), subst(arrow.tgt))

    @staticmethod
    def target_cast(Tgt, y):
        if not isinstance(Tgt, Var):
            return io.cast(y, Tgt)
        return y


class Hom(Arrow, metaclass=HomFunctor):
    """
    Hom functor: maps type pairs to their callable types.

    The type `Hom(A, B)` describes callables with input in `A`
    and output in `B`, it can be used as a decorator to type
    a function definition.

    Example:
    --------
    .. code::

        >>> @Hom(Int, Str):
        ... def bar(n):
        ...     return n * "|"
        ...
        >>> bar
        Int -> Str : bar
        >>> bar(8)
        Str : '||||||||'
    """

    Object = HomObject

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

    @classmethod
    def id(cls, A):
        idA = cls(A, A)(())
        idA.__name__ = "id"
        return idA

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

        **Note:**
        Composition is made associative by storing the sequence
        of functions in a flat tuple. This also avoids nesting
        function closures.
        """
        src = f.src
        tgt = (fs[-1] if len(fs) else f).tgt
        pipe = sum((list(fi._pipe) for fi in (f, *fs)), [])
        pipe = cls(src, tgt)(tuple(pipe))
        pipe.__name__ = cls._composed_name_(f, *fs)
        return pipe

    @classmethod
    def eval(cls, x: A, f: callable[A, B]) -> B:
        """
        Evaluate `f` on input `x`.
        """
        return f(x)

    @classmethod
    def partial(cls, f, *xs):
        """
        Partial function applied to n-ary input `xs` for n < arity.

        Example
        -------
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

            f_xs = functools.partial(f, *xs)
            f_xs.__name__ = f"{f.__name__} " + " ".join((str(x) for x in xs))
            return cls(src, f.tgt)(f_xs)

        elif len(xs) == f.arity:
            f_xs = functools.partial(f, *xs)
            f_xs.__name__ = f"{f.__name__} " + " ".join((str(x) for x in xs))
            return cls((), f.tgt)(f_xs)

        raise TypeError(
            f"Cannot partially call {f.arity} function on " + f"{len(xs)}-ary input"
        )

    @classmethod
    def _get_name_(cls, A, B):

        def name_one(T):
            if hasattr(T, "_head_") and isinstance(T._head_, ArrowFunctor):
                return "(" + T.__name__ + ")"
            elif hasattr(T, "__name__"):
                return T.__name__
            else:
                return str(T)

        def name_arg(C):
            if isinstance(C, tuple):
                names = tuple(name_one(T) for T in C)
                if "..." in names:
                    name = "(" + ", ".join(names) + ")"
                else:
                    name = " -> ".join(names)
                return name
            return name_one(C)

        return name_arg(A) + " -> " + name_arg(B)

    @classmethod
    def _composed_name_(cls, *fs):
        name = lambda f: f.__name__ if hasattr(f, "__name__") else str(f)
        if len(fs) <= 4:
            return " . ".join(name(f) for f in fs[::-1])
        else:
            return "(" + name(fs[0]) + " . ... . " + str(name[-1]) + ")"

    @classmethod
    def _parse_input_(cls, A, B):
        """
        Parse N-ary source types.
        """
        if type(B) is tuple:
            tgt = Type.Prod(*B)
        else:
            tgt = B

        if isinstance(A, Type.Prod):
            src, arity = A, len(A._tail_)
        elif isinstance(A, type):
            # A -> B
            src, arity = A, 1
        elif isinstance(A, tuple):
            # (A1, ..., An) -> B
            src, arity = Type.Prod(*A), len(A)
        else:
            raise io.TypeError("source", A, Type | Iterable[Type])
        return src, tgt, arity
