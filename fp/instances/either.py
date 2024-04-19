from fp.meta import Type, NFunctor, Monad
from .prod import Prod
from .hom import Hom
from .wrap import Wrap

from colorama import Fore

import typing

class Either(Wrap, metaclass=Monad):
    """
    Direct sum of types (union).
    """
    class _top_(Wrap._top_):
        
        def __init__(self, x):
            union = self._wrapped_.__args__
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
    def new(cls, *As):
        return super().new(typing.Union[*As])
    
    @classmethod
    def fmap(cls, *fs):

        src = Either(*(f.src for f in fs), ...)
        tgt = Either(*(f.tgt for f in fs), ...)

        @Hom(src, tgt)
        def either_f(x):
            if x._i_ < len(fs):
                return fs[x._i_](x.data)
            return x

        either_f.__name__ = Either._get_name_(*fs)

        return either_f
        
    def _post_new_(EA, *As):
        return super()._post_new_(typing.Union[*As])

    @classmethod
    def _get_name_(cls, *As):
        name = lambda A: (A.__name__ if hasattr(A, '__name__') else str(A))
        return "(" + " | ".join(name(A) for A in As) + ")"
