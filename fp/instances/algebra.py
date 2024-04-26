import re
import fp.io as io
from fp.cartesian import Type, Hom

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
            op = cls.lift_op(T, getattr(T, op_name), arity=r)
            setattr(T, op_name, op)
            # alias operators: 'add', ...
            alias = re.match(r'__(\w*)__', op_name).groups()
            op.__name__ = alias[0] if len(alias) else op_name
            src = T if r == 1 else tuple([T] * r)
            setattr(T, op.__name__, Hom(src, T)(op))

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

