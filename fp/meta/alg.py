from .type  import TypeMeta
from .arrow import Arrow

#--- Numerical types ---

class RingMeta(TypeMeta):
    """ Ring type class. """

    def __new__(cls, name, bases, dct):
        T = super().__new__(cls, name, bases, dct)
        # operators
        T.__add__ = cls.op_method(T, T.__add__)
        T.__sub__ = cls.op_method(T, T.__sub__)
        T.__mul__ = cls.op_method(T, T.__mul__)
        T.__neg__ = cls.op_method(T, T.__neg__, arity=1)
        # operator aliases
        names   = ['add', 'sub', 'mul', 'neg']
        for name in names:
            op = getattr(T, f'__{name}__')
            op.__name__ = op.__name__.replace('__', '')
            setattr(T, name, op)
        return T
    
    @staticmethod
    def op_method(T, op, arity=2):
        """ Binary operator with output cast to T. """
        _op_ = lambda *xs : T.cast(op(*xs))
        _op_.__name__ = op.__name__
        Tn = tuple([T] * arity)
        return Arrow(Tn, T)(_op_)

class AlgMeta(RingMeta):

    """ Algebra type class. """
    def __new__(cls, name, bases, dct):
        T = super().__new__(cls, name, bases, dct)
        T.__truediv__ = cls.op_method(T, T.__truediv__)
        div = T.__truediv__
        div.__name__ = 'div'
        T.div = div
