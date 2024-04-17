import torch
from ._wrap_alg import WrapRing
from fp.instances import Type, Hom, Wrap, Alg, Ring


class TensorBase:

    # --- Tensor attributes ---
    
    def dim(self):
        return self.data.dim()
    
    @property
    def shape(self):
        return self.data.shape

    @property
    def dtype(self):
        return self.data.dtype

    @property
    def device(self):
        return self.data.device

    # --- Type casts ---

class Tensor(WrapRing(torch.Tensor), TensorBase):

    @classmethod
    def sparse(cls, shape, indices, values=None):
        ij = (
            indices
            if isinstance(indices, torch.Tensor)
            else torch.tensor(indices, dtype=torch.long)
        )
        val = torch.ones([ij.shape[-1]]) if isinstance(values, type(None)) else values
        t = torch.sparse_coo_tensor(ij, val, size=shape)
        return cls(t)

    # --- Tensor casts ---

    def float(self):
        return self.__class__(self.data.float())

    def cfloat(self):
        return self.__class__(self.data.cfloat())

    def long(self):
        return self.__class__(self.data.long())

    def double(self):
        return self.__class__(self.data.double())

    def is_floating_point(self):
        return self.data.is_floating_point()

    def is_complex(self):
        return self.data.is_complex()

    # ---

    def norm(self, p="fro", dim=None):
        return self.data.norm(p, dim)

    def __getitem__(self, idx):
        return Tensor(self.data[idx])

    def __str__(self):
        return (
            str(self.data)
            .replace("tensor(", "")
            .replace("\n       ", "\n")
            .replace(")", "")
        )

    def __repr__(self):
        return str(self)

    def __len__(self):
        return int(torch.tensor(self.data.shape).prod())

    # --- tensor product ---

    def otimes(self, other):
        """
        Tensor product of two instances.

        The tensor product xy of two vectors x and y is defined by:

            xy[i, j] = x[i] * y[j]

        In general, if x and y are of shape A and B respectively,
        the tensor product xy will be of shape [*A, *B].
        """
        x, y = self.data.flatten(), other.data.flatten()
        X = x.repeat_interleave(y.numel(), 0)
        Y = y.repeat(x.numel())
        xy = (X * Y).view([*self.data.shape, *other.data.shape])
        return Tensor(xy)

    def __or__(self, other):
        return self.otimes(other)

    # --- right actions ---

    def __rmul__(self, other):
        return self.__mul__(other)

    def __radd__(self, other):
        return self.__add__(other)

    # --- constructors ---

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

    @classmethod
    def range(cls, n):
        return cls(torch.arange(n))
