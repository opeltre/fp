from .algebra import Monoid
from .num import Int
from fp.cartesian import Hom
from fp import utils


class Str(str, metaclass=Monoid):

    def __str__(self):
        return super().__repr__()

    @classmethod
    def cast(cls, s):
        if type(s) is cls:
            return s
        if type(s) is str:
            return cls(s)
        raise utils.CastError(cls, s)


Str.len = Hom(Str, Int)(len)
