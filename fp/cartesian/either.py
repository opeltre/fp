from __future__ import annotations
from fp.meta import Type, NFunctor, Monad
import fp.io as io
from .prod import Prod
from .hom import Hom

from colorama import Fore

import typing


class Either(Type, metaclass=Monad):
    """
    Direct sum of types (union).

    Example:
    --------
    .. code::

        >>> Either(Int, Str)
        Either : (Int | Str)
        >>> (Int | Str) is Either(Int, Str)
        True
        >>> x = List(int | str)(["Hello", 12, "World!", 8])
        >>> foo = Hom(str, int)(len)
        >>> bar = Hom(int, str)(lambda x: "|" * x)
        ### functorial map: type-wise application
        >>> Either.fmap(bar, foo)
        (int | str | ...) -> (str | int | ...) : (λ | len | ...)
        >>> List.fmap(Either.fmap(bar, foo))(x)
        List (str | int | ...) : [1 : 5, 0 : ||||||||||||, 1 : 6, 0 : ||||||||]
    """
    class Object:
        
        def __init__(self, x):
            union = self._union_.__args__
            for i, A in enumerate(union):
                if isinstance(x, A):
                    self._i_ = i
                    self.data = x
                    break

        def __repr__(self):
            prefix = Fore.YELLOW + f"{self._i_} : " + Fore.RESET
            data = str(self.data).replace("\n", "\n" + " " * len(prefix))
            return prefix + data

        @classmethod
        def cast(E, x):
            for i, Ti in enumerate(E._tail_):
                try:
                    return E(io.cast(x, Ti))
                except:
                    pass
             
    @classmethod
    def new(cls, *As):
        """
        Type union.
        """
        return super().new(typing.Union[*As])
    
    def _post_new_(EA, *As):
        EA._union_ = typing.Union[*As]
        return EA

    @classmethod
    def fmap(cls, *fs):
        """
        Apply a mapping on each case.
        """
        if fs[-1] is ...:
            fs = (*fs[:-1], lambda x:x)
            src = Either(*(f.src for f in fs[:-1]), ...)
            tgt = Either(*(f.tgt for f in fs[:-1]), ...)
            name = Either._get_name_(*fs, "...")
        else:
            src = Either(*(f.src for f in fs))
            tgt = Either(*(f.tgt for f in fs))
            name = Either._get_name_(*fs)

        @Hom(src, tgt)
        def either_f(x):
            if x._i_ < len(fs):
                return fs[x._i_](x.data)

        either_f.__name__ = name

        return either_f
    
    @classmethod
    def unit(cls, x: Var("A")) -> cls(Var("A"), ...):
        return cls("A", ...)(x)

    @classmethod
    def join(cls, EEx: cls(cls("A", ...), ...)) -> cls("A", ...):
        """
        Access unwrapped either value.
        """
        tgt = cls._tail_[0] 
        return tgt(x)
    
    @classmethod
    def gather(cls, f: Callable, *fs: Callable) -> Callable:
        """
        Universal property of categorical sums.

        Given a collection of arrows with the same target `Y`,
        return an arrow from the sum of sources to `Y`.

            (A -> Y, B -> Y, ...) -> (A | B | ...)  ->  Y

        The initial arrow from `(A | B | ...)` has the input maps as 
        as restrictions.
        """
        F = (f, *fs)
        src = cls(*(fi.src for fi in F))
        tgt = f.tgt

        @Hom(src, tgt)
        def gather_f(x):
            """Map a sum type `(A | B | ...)` to a target `Y`."""
            return F[x._i_](x.data)
        gather_f.__name__ = "gather " + Either._get_name_(f, *fs)
        return gather_f

    def __getitem__(E, i:int | slice):
        if isinstance(i, int):
            return E._tail_[i]
        return E.__class__(*E._tail_[i])

    @classmethod
    def _get_name_(cls, *As):
        name = lambda A: (A.__name__ if hasattr(A, '__name__') else str(A))
        return "(" + " | ".join(name(A) for A in As) + ")"

class Bottom:
    
    def __new__(cls, *xs):
        raise io.CastError(cls, xs)

Either.Unit = Type("∅ ", (Bottom,), {})
