import torch

from .tensor import Tensor, TensorBase
from .shape import Torus
from fp.instances import Ring

class TypedTensor(Tensor, metaclass=Ring):
    
    shape: Tensor
    domain : Torus 

    def __init__(self, data):
        super().__init__(data)
        S = self.shape
        if isinstance(data, Tensor):
            data = data.data
        if not isinstance(data, torch.Tensor):
            data = torch.tensor(data)
        if S == tuple(data.shape) or S == list(data.shape):
            self.data = data
        elif len(data.shape) == 0:
            self.data = data
        elif S[-len(data.shape) :] == list(data.shape):
            self.data = data
        else:
            self.data = data.reshape(S)

    def otimes(self, other):
        """
        Tensor product of two instances.

        The tensor product xy of vectors x and y is defined by:

            xy[i, j] = x[i] * y[j]

        In general, if x : Tens(A) and y : Tens(B) then xy
        is of type Tens([*A, *B])
        """
        TA, TB = self.__class__, other.__class__
        TAB = cls([*TA.shape, *TB.shape])
        xy = Tensor.otimes(self, other)
        return TAB(xy)

    @classmethod
    def zeros(cls, **ks):
        super().zeros(cls.shape, **ks)

    @classmethod
    def ones(cls, **ks):
        super().ones(cls.shape, **ks)

    @classmethod
    def randn(cls, **ks):
        super().randn(cls.shape, **ks)

    @classmethod
    def rand(cls, **ks):
        super().rand(cls.shape, **ks)

    @classmethod
    def range(cls):
        return cls(torch.arange(cls.domain.size).view(cls.shape))

    @classmethod
    def embed(cls, *ds):
        """Linear embedding Tens B -> Tens A for B subface of A.

        This algebra morphishm extends a tensor on the restriction
        `B = [A[di] for di in ds]` by:

            f_a[di] = f_b[i] for i, di in enumerate(d)
            f_a[dj] = 0      for dj not in d

        This is the pullback of the coordinate map `cls.domain.res(*ds)`,
        and the linear adjoint of `cls.proj(*ds)`.
        """
        res = cls.domain.res(*ds)
        return Tens.cofmap(res)

    @classmethod
    def proj(cls, *ds):
        """Partial integration Tens A -> Tens B for B subface of A.

        This linear map projects onto tensors of shape
        `B = [A[di] for di in ds]` by:

            g_b[xb] = sum_{xa[ds] = xb} g_a[xa]

        This is the pushforward of the coordinate map `cls.domain.res(*ds)`
        (acting on measures), and the adjoint of the algebra morphism `cls.embed(*ds)`.
        """
        return cls.embed(*ds).t()
