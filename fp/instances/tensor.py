import torch
from fp.meta import Arrow, ArrowMeta, RingMeta, TypeMeta, Functor
from .wrap import Wrap

binops  = ['__add__', '__sub__', '__mul__', '__truediv__']

class WrapRing(Wrap):

    lifts = {name     : lambda a: Arrow((a, a), a) for name in binops} \
          | {'__neg__': lambda a: Arrow(a, a)}


class Tensor(WrapRing(torch.Tensor), metaclass=RingMeta):
    
    
    def __repr__(self):
        return (str(self.data).replace("tensor(", "")
                              .replace("\n       ", "\n")
                              .replace(")", ""))
    @classmethod
    def zeros(cls, ns, **ks):
        return cls(torch.zeros(ns, **ks))

    @classmethod
    def ones(cls, ns, **ks):
        return cls(torch.ones(ns, **ks))

    @classmethod
    def randn(cls, ns, **ks):
        return cls(torch.randn(ns, **ks))

    @classmethod
    def rand(cls, ns, **ks):
        return cls(torch.rand(ns, **ks))


class TensMeta (RingMeta):

    def __new__(cls, name, bases, dct):
        if 'shape' in dct:
            name = f'Tens ({",".join([str(n) for n in shape])})'
            return super().__new__(cls, name, bases, dct)


class Tens(Functor):
    
    class Scalar (Tensor):

        shape = ()

        def __repr__(self):
            return (str(self.data)
                        .replace("tensor(", "")
                        .replace("\n       ", "\n")
                        .replace(")", ""))

        @classmethod
        def zeros(cls, **ks):
            return cls(torch.zeros(cls.shape, **ks))

        @classmethod
        def ones(cls, **ks):
            return cls(torch.ones(cls.shape, **ks))

        @classmethod
        def randn(cls, **ks):
            return cls(torch.randn(cls.shape, **ks))

        @classmethod
        def rand(cls, **ks):
            return cls(torch.rand(cls.shape, **ks))

    def __new__(cls, shape):
        name = cls.name(shape)
        bases, dct = cls.Scalar.__bases__, dict(cls.Scalar.__dict__)
        dct['shape'] = shape
        TA = RingMeta(name, bases, dct)
        return TA

    @classmethod
    def name(cls, shape):
        return f'Tens {"x".join(str(n) for n in shape)}'

    @classmethod
    def fmap(cls, f):
        pass


class Linear(metaclass=ArrowMeta):

    def __new__(cls, A, B):
        
        class LinAB (Tens([B, A]), Arrow(Tens([A]), Tens([B]))):
            
            functor = Linear
            input = (A, B)

            def __init__(self, matrix, name=f'mat {B} x {A}'):
                cls = self.__class__
                # Arrow(Tens([A]), Tens([B])) attributes
                self.call = lambda x : cls.matvec(matrix, x)
                self.__name__ = name
                # Tens([B, A]) attributes
                mat = matrix.data if isinstance(matrix, Tensor) else matrix
                super().__init__(mat)

            
            @classmethod
            def matvec (cls, mat, x):
                if isinstance(x, Tensor):
                    return mat.data @ x.data
                elif isinstance(x, torch.Tensor):
                    return mat.data @ x.data
            
            def __repr__(self):
                return self.__name__
        
        return LinAB

    def __init__(self, A, B):
        pass

    @classmethod
    def compose (cls, f, g):
        """ Composition of matrices """
        print("Linear.compose")
        return cls(f.tgt.shape[0], g.src.shape[0])(f.data @ g.data)

    @classmethod
    def name(cls, A, B):
        shape = lambda S : 'x'.join(str(n) for n in S)
        return f'Linear {A} -> {B}'