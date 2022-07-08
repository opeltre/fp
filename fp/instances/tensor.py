import torch
from fp.meta import Arrow, ArrowMeta, RingMeta, TypeMeta, Functor
from .wrap import Wrap

binops  = ['__add__', '__sub__', '__mul__', '__truediv__']

class WrapRing(Wrap):

    lifts = {name     : lambda a: Arrow((a, a), a) for name in binops} \
          | {'__neg__': lambda a: Arrow(a, a)}


class Tensor(WrapRing(torch.Tensor), metaclass=RingMeta):
    
    def dim (self):
        return self.data.dim()

    def __getitem__(self, idx):
        return Tensor(self.data[idx])

    def __repr__(self):
        return (str(self.data).replace("tensor(", "")
                              .replace("\n       ", "\n")
                              .replace(")", ""))
    
    def __len__(self):
        return int(torch.tensor(self.data.shape).prod())

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