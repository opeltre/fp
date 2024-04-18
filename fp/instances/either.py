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
            data = repr(self.data).replace("\n", "\n" + " " * len(prefix))
            return prefix + data
             
    @classmethod
    def new(cls, *As):
        return super().new(typing.Union[*As])

    def _post_new_(EA, *As):
        return super()._post_new_(typing.Union[*As])

    @classmethod
    def _get_name_(cls, *As):
        return "(" + " | ".join(A.__name__ for A in As) + ")"
