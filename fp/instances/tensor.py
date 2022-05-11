import torch
from fp.meta import Arrow, RingMeta, TypeMeta
from .wrap import Wrap

Tens    = torch.Tensor
binops  = ['__add__', '__sub__', '__mul__', '__truediv__']

class WrapRing(Wrap):

    lifts = {name     : lambda a: Arrow((a, a), a) for name in binops} \
          | {'__neg__': lambda a: Arrow(a, a)}


class Tensor(WrapRing(Tens), metaclass=RingMeta):
    
    
    def __repr__(self):
        return (str(self.data).replace("tensor(", "")
                              .replace("\n       ", "\n")
                              .replace(")", ""))