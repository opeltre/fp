from __future__ import annotations

import typing
from types import ModuleType

from fp.cartesian import Type, Hom

from .backend.wrap_alg import Backend

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
        Numpy = self.__class__.Numpy
        data = Numpy._backend_.asarray(self.data).copy()
        return Numpy(data)

    def torch(self):
        Torch = self.__class__.Torch
        return Torch(Torch.asarray(self.numpy().data))

    def jax(self):
        Jax = self.__class__.Jax
        return Jax(Jax.asarray(self.numpy().data))

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

