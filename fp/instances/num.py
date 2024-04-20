import re

from fp.meta import Type
import fp.io as io
from .hom import Hom

class Eq(Type):

    def __init__(T, name, bases, dct):
        # eq : T -> T -> Bool
        if name == "Bool":
            cls.Bool = T
        if "Bool" in dir(cls):
            eq = T.lift_op(T, T.__eq__, tgt=cls.Bool)
            eq.__name__ = "eq"
            T.eq = Type.Hom((T, T), cls.Bool)(eq)

class Operad(Type):

    _operators_ : list[tuple[str, int]]

    def __init__(T, name="A", bases=(), dct={}):
        super().__init__(name, bases, dct)
        cls = T.__class__
        for op_name, r in cls._operators_:
            # lift operator: '__add__', ...
            op = cls.lift_op(T, getattr(T, op_name))
            setattr(T, op_name, op)
            # alias operators: 'add', ...
            alias = re.match(r'__(\w*)__', op_name).groups()
            op.__name__ = alias[0] if len(alias) else op_name
            setattr(T, op.__name__, Hom(tuple([T] * r), T)(op))

    @staticmethod
    def lift_op(T, op, tgt=None, arity=2):
        """N-ary operator with output cast to target."""
        tgt = tgt if tgt else T
        if arity == 1:

            def _op_(x):
                y = op(x)
                return y if isinstance(y, tgt) else io.cast(y, tgt)

        elif arity == 2:

            def _op_(x1, x2):
                y = op(x1, x2)
                return y if isinstance(y, tgt) else io.cast(y, tgt)

        else:

            def _op_(*xs):
                y = op(*xs)
                return y if isinstance(y, tgt) else io.cast(y, tgt)

        _op_.__name__ = op.__name__
        return _op_


class Monoid(Operad):
    """Monoid type class."""
    
    _operators_ = [('__add__', 2)]


# --- Numerical type classes ---

class Ring(Monoid):
    """Ring type class."""
    
    _operators_ = [
        ('__add__', 2),
        ('__sub__', 2),
        ('__mul__', 2),
        ('__neg__', 1)
    ]

    def __init__(T, name="R", bases=(), dct={}):
        super().__init__(name, bases, dct)
        cls = T.__class__
        # eq : T -> T -> Bool
        if name == "Bool":
            cls.Bool = T
        if "Bool" in dir(cls):
            eq = T.lift_op(T, T.__eq__, tgt=cls.Bool)
            eq.__name__ = "eq"
            T.eq = Type.Hom((T, T), cls.Bool)(eq)

    @staticmethod
    def lift_op(T, op, tgt=None, arity=2):
        """N-ary operator with output cast to target."""
        tgt = tgt if tgt else T
        if arity == 1:

            def _op_(x):
                y = op(x)
                return y if isinstance(y, tgt) else io.cast(y, tgt)

        elif arity == 2:

            def _op_(x1, x2):
                y = op(x1, x2)
                return y if isinstance(y, tgt) else io.cast(y, tgt)

        else:

            def _op_(*xs):
                y = op(*xs)
                return y if isinstance(y, tgt) else io.cast(y, tgt)

        _op_.__name__ = op.__name__
        return _op_


class Alg(Ring):
    """Algebra type class."""

    def __init__(T, name, bases, dct):
        super().__init__(name, bases, dct)
        cls = T.__class__
        T.__truediv__ = cls.lift_op(T, T.__truediv__)
        div = Type.Hom((T, T), T)(T.__truediv__)
        div.__name__ = "div"
        T.div = div

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


class Str(str, metaclass=Monoid):
    
    def __str__(self):
        return super().__repr__() 

    
Str.len = Hom(Str, Int)(len)
