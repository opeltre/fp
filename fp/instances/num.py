import fp.io as io
from fp.cartesian import Type, Hom
from .algebra import Ring, Alg, Monoid

#----- Instances ------

class Bool(int, metaclass=Ring):
    """Boolean values."""

    def __new__(cls, x):
        if x == 1:
            return super().__new__(cls, 1)
        if x == 0:
            return super().__new__(cls, 0)
        raise TypeError(f"Invalid boolean value {x}")

    @classmethod
    def cast(cls, x):
        return Bool(1) if x else Bool(0)

    def __neg__(self):
        return Bool(0 if self else 1)

    def __bool__(self):
        return super().__eq__(1)
    
    def __str__(self):
        return "1" if self else "0"

    def __repr__(self):
        return "True" if self else "False"


class Int(int, metaclass=Ring):

    def __str__(self):
        return super().__repr__()


class Float(float, metaclass=Alg):

    def __str__(self):
        return super().__repr__()
