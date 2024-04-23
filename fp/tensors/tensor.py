from __future__ import annotations

from .backend import torch, np, jnp

import typing
from types import ModuleType

from ._wrap_alg import WrapRing, Backend, TorchBackend, NumpyBackend, JaxBackend
from fp.instances import Type, Hom, Wrap, Alg, Ring


class TensorBase:
    
    _backend_ : Backend
    _module_ : ModuleType

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
    
    @property
    def size(self):
        return self.data.size

    # --- access --- 

    def __getitem__(self, idx):
        return Tensor(self.data[idx])

    def __len__(self):
        return int(torch.tensor(self.data.shape).prod())
    
    def __iter__(self):
        return self.data.__iter__()
    
    def reshape(self, *shape:int | tuple[int]):
        return self.__class__(self.data.reshape(shape))
    
    # --- reductions ---

    def prod(self, *xs, **ks):
        return self.__class__(self.data.prod())

    def sum(self, *xs, **ks):
        return self.__class__(self.data.sum())

    # --- backend switch ---

    def numpy(self):
        data = NumpyBackend.asarray(self.data).copy()
        return Numpy(data)

    def torch(self):
        return Torch.asarray(self.numpy().data)

    def jax(self):
        return Jax.asarray(self.numpy().data) 

    # --- repeats ---

    def repeat(self, repeats: int | typing.Iterable[int]) -> TensorBase:
        """
        Repeat (interleave) elements of the input array.

        Behaviour of `numpy.repeat`, see `tile` for the torch version of 
        `repeat`.
        """
        cls = self.__class__
        repeats = repeats if type(repeats) is int else cls(repeats).data
        repeat = getattr(self._module_, self._backend_.repeat)
        return cls(repeat(self.data, repeats))

    def tile(self, ntiles: tuple[int,...]):
        """
        Tile input array across given dimension-wise repetitions.
        """
        repeat = getattr(self._module_, self._backend_.tile)
        return self.__class__(repeat(self.data, ntiles))

    # --- tensor product --- 

    def __or__(self, other):
        return self.otimes(other)

    # --- right actions ---

    def __rmul__(self, other):
        return self.__mul__(other)

    def __radd__(self, other):
        return self.__add__(other)

    # --- constructors ---
    
    @classmethod
    def asarray(cls, data: typing.Any) -> cls:
        return cls(cls._module_.asarray(data))

    @classmethod
    def zeros(cls, ns, **ks):
        return cls(cls._module_.zeros(ns, **ks))

    @classmethod
    def ones(cls, ns, **ks):
        return cls(cls._module_.ones(ns, **ks))

    @classmethod
    def randn(cls, ns, **ks):
        return cls(cls(torch.randn(ns, **ks)))

    @classmethod
    def rand(cls, ns, **ks):
        return cls(torch.rand(ns, **ks))

    @classmethod
    def range(cls, n, **ks):
        return cls(cls._module_.arange(n, **ks))

    # --- tensor product ---

    def otimes(self, other):
        """
        Tensor product of two instances.

        The tensor product `xy` of two vectors `x` and `y` is defined by:

        .. code::

            xy[i, j] = x[i] * y[j]

        In general, if `x` and `y` are of shape `A` and `B` respectively,
        the tensor product xy will be of shape `(*A, *B)`. Its values are
        obtained by `Tensor.otimes(x.flatten(), y.flatten())`.

        **Example**
        ..code:: 

            >>> ints = Numpy.range(4) + 1
            >>> table = ints | ints
            >>> Numpy.otimes(ints, ints)
            Numpy : [[ 1  2  3  4]
                     [ 2  4  6  8]
                     [ 3  6  9 12]
                     [ 4  8 12 16]]
        """
        cls = self.__class__
        flatten = cls.flatten
        x, y = flatten(self), flatten(other)
        X = x.repeat(y.size)
        Y = y.tile(x.size)
        xy = cls.reshape((X * Y), (*self.shape, *other.shape))
        return xy


class Numpy(NumpyBackend(np.ndarray), TensorBase):

    def is_floating_point(self):
        return self.data.is_floating_point()

    def is_complex(self):
        return self.data.is_complex()

    def norm(self, p="fro", dim=None):
        return self.data.norm(p, dim)

class Jax(JaxBackend(JaxBackend.Array), TensorBase):
    ...

class Torch(TorchBackend(torch.Tensor), TensorBase):
    
    @property
    def size(self):
        return self.data.numel()
    
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

    def is_floating_point(self):
        return self.data.is_floating_point()

    def is_complex(self):
        return self.data.is_complex()

    def norm(self, p="fro", dim=None):
        return self.data.norm(p, dim)

    def tile(self, repeats: tuple[int,...]):
        return self.__class__(self.data.repeat(repeats)) 

    # ---

    def __str__(self):
        return (
            str(self.data)
            .replace("tensor(", "")
            .replace("\n       ", "\n")
            .replace(")", "")
        )

    def __repr__(self):
        return str(self)

class Tensor(Torch):
    ...
