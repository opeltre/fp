import torch

from .tensor import Tensor, WrapRing
from .shape  import Torus
from fp.meta import ArrowMeta, Arrow, Functor, Bifunctor
from fp.meta import RingMeta

class TensorMod(Functor):
    
    def __new__(cls, N):

        class TensorMod_N(Tensor):

            modulus = N
            
            def __init__(self, data):
                super().__init__
                self.data = self.data % self.modulus
                
            @classmethod
            def cast(cls, x):
                if not isinstance(x, (torch.Tensor, Tensor)):
                    x = torch.Tensor(x)
                return cls(x.data % cls.modulus)
        
        return TensorMod_N
    
    @classmethod
    def fmap(cls, f):
        pass
    