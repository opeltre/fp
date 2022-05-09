import abc
from .arrow import Arrow
from .type  import Type, TypeMeta

class AlgMeta(TypeMeta):
    """ Algebra type class. """

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
        def _op_(x, y):
            z = op(x, y)
            return cls.cast(T, z)       
        return _op_

class Alg(metaclass=AlgMeta):

    @abc.abstractmethod
    def __add__(self, other):
        ...

    @abc.abstractmethod
    def __sub__(self, other):
        ...
    
    @abc.abstractmethod
    def __mul__(self, other):
        ...

    @abc.abstractmethod
    def __div__(self, other):
        ...

    @abc.abstractmethod
    def __neg__(self, other):
        ...