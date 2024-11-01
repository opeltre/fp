import numpy as np

from types import ModuleType
from typing import Callable
from fp.base import struct, List, Str

# ====== Interfaces : populated during __init__.py ======

INTERFACES = {}


@struct
class DtypeTable:
    """
    Declare aliases to dtype-casts.

    Args:
        bound_to (str) : name of the :class:`Interface` attribute owning
            the type cast methods (e.g. `module` for jax and numpy, and
            `Array = torch.Tensor` for torch).
        int32 (str) : name of the `int` cast method,
        int64 (str) : name of the `long` cast method,
        float32 (str) : a.k.a. `float`
        float64 (str) : a.k.a. `double`
        complex64 (str) : a.k.a. `cfloat`
        complex128 (str) : a.k.a. `cdouble`
    """

    float32: str = "float32"
    float64: str = "float64"
    complex64: str = "complex64"
    complex128: str = "complex128"
    int32: str = "int32"
    int64: str = "int64"


@struct
class Interface:
    """Declares bindings to a numerical backend.

    `Interface` objects can be mapped to a `TensorBase <= Ring` subclass, by
    any functor wrapping over the `interface.Array` type.
    See :class:`Backend` for such a functor.

    The summarized `struct` layout makes it easier to spot and enumerate what
    are mere naming differences.

    Args:
        module (ModuleType): python module
        Array (type): base array class, e.g. `np.ndarray`
        asarray (callable): default constructor
        dtypes (DtypeTable): a struct holding dtype aliases, e.g.
            `dtypes.float64 = "double"` for torch,
        dtypes_bind (str) : name of the `Interface` attribute owning the
            cast methods, e.g. `"module"` or `"Array"`.
        repeat (str): name of `"repeat"` method (`"repeat_interleave"` for torch)
        tile (str): name of `"tile"` method (`"repeat"` for torch)
    """

    module: ModuleType
    Array: type
    asarray: Callable
    dtypes: DtypeTable = DtypeTable()
    dtypes_bind: str = "module"
    # aliases
    repeat: Str = "repeat"
    tile: Str = "tile"

    def dtype_cast(self, dtype: str) -> Callable:
        """Return cast method `dtype : Array -> Array`."""
        owner = getattr(self, self.dtypes_bind)
        alias = getattr(self.dtypes, dtype)
        return getattr(owner, alias)

    def __repr__(self):
        return self.module.__name__

    def __str__(self):
        return self.module.__name__
