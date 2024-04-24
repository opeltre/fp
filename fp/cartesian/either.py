from __future__ import annotations
from fp.meta import Type, NFunctor, Monad
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
    class _top_:
        
        def __init__(self, x):
            union = self._wrapped_.__args__
            for i, A in enumerate(union):
                if isinstance(x, A):
                    self._i_ = i
                    self.data = x
                    break

        def __str__(self):
            prefix = Fore.YELLOW + f"{self._i_} : " + Fore.RESET
            data = str(self.data).replace("\n", "\n" + " " * len(prefix))
            return prefix + data
             
    @classmethod
    def new(cls, *As):
        """
        Type union.
        """
        return super().new(typing.Union[*As])
    
    def _post_new_(EA, *As):
        return super()._post_new_(typing.Union[*As])

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
    def _get_name_(cls, *As):
        name = lambda A: (A.__name__ if hasattr(A, '__name__') else str(A))
        return "(" + " | ".join(name(A) for A in As) + ")"