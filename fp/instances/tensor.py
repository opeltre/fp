import torch
from fp.meta import Arrow, RingMeta, TypeMeta, Functor
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


class Tens(Functor):
    
    def __new__(cls, A):

        class TA (WrapRing(torch.Tensor), metaclass=RingMeta):
            
            shape = A

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
        
        return TA

    @classmethod
    def fmap(cls, f):
        pass