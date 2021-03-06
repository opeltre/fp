from .type  import TypeMeta
from .arrow import Arrow

#--- Numerical types ---

class RingMeta(TypeMeta):
    """ Ring type class. """

    def __new__(cls, name, bases, dct):
        T = super().__new__(cls, name, bases, dct)
        return T
    
    def __init__(T, name, bases, dct):
        cls = T.__class__
        # operators
        T.__add__ = cls.op_method(T, T.__add__)
        T.__sub__ = cls.op_method(T, T.__sub__)
        T.__mul__ = cls.op_method(T, T.__mul__)
        T.__neg__ = cls.op_method(T, T.__neg__, arity=1)
        # operator aliases
        names   = ['add', 'sub', 'mul', 'neg']
        arities = [2] * 3 + [1]
        for (n, r) in zip(names, arities):
            op = getattr(T, f'__{n}__')
            op = (Arrow(T, T)(op) if r == 1
                    else Arrow(tuple([T] * r), T)(op))
            op.__name__ = n
            setattr(T, n, op)
        # eq : T -> T -> Bool   
        if name == "Bool":
            cls.Bool = T
        if "Bool" in dir(cls):
            eq = T.op_method(T, T.__eq__, tgt=cls.Bool)
            eq.__name__ = 'eq'
            T.eq = Arrow((T, T), cls.Bool)(eq)
            
                  
    @staticmethod
    def op_method(T, op, tgt=None, arity=2):
        """ N-ary operator with output cast to target. """
        tgt = tgt if tgt else T
        if arity == 1:
            def _op_(x):
                y = op(x)
                return y if isinstance(y, tgt) else tgt.cast(y)
        elif arity == 2:
            def _op_(x1, x2):
                y = op(x1, x2)
                return y if isinstance(y, tgt) else tgt.cast(y)
        else: 
            def _op_(*xs):
                y = op(*xs)
                return y if isinstance(y, tgt) else tgt.cast(y)
        _op_.__name__ = op.__name__
        return _op_


class AlgMeta(RingMeta):
    """ Algebra type class. """
    def __new__(cls, name, bases, dct):
        T = super().__new__(cls, name, bases, dct)
        T.__truediv__ = cls.op_method(T, T.__truediv__)
        div = Arrow((T, T), T)(T.__truediv__)
        div.__name__ = 'div'
        T.div = div
        return T


class Bool(int, metaclass=RingMeta):
    """ Boolean values. """

    def __new__(cls, x):
        if x == 1:
            return super().__new__(cls, 1)
        if x == 0:
            return super().__new__(cls, 0)
        raise TypeError(f'Invalid boolean value {x}')

    @classmethod
    def cast(cls, x):
        return Bool(1) if x else Bool(0)
    
    def __repr__(self):
        return 'True' if self else 'False'
    
    def __neg__(self):
        return Bool(0 if self else 1)

    def __bool__(self):
        return super().__eq__(1)
