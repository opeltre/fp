import torch
import jax
import numpy as np

from types import ModuleType
from typing import Callable

from fp.cartesian import Type, Hom, Prod
from fp.instances import Lift, Wrap, Alg, Ring
from fp.instances import struct, List, Str

import os

signature = lambda n : lambda A: Hom(tuple([A] * n), A)

@struct
class Interface:
    module : ModuleType
    Array : type
    asarray : Callable
    dtypes : List(Str)
    # aliases
    repeat : Str = "repeat"
    tile : Str = "tile"

tensor_methods = [
    # reshapes
    Lift("__add__", 2),
    Lift("__sub__", 2),
    Lift("__mul__", 2),
    Lift("__truediv__", 2),
    Lift("__neg__", 1),
    # reshapes
    Lift("__flatten__", 1),
    Lift("reshape", lambda T: Hom((T, tuple), T), 0, flip=1),
]

class WrapRing(Ring, Wrap):

    _lifted_methods_ = tensor_methods

class EitherRing(Ring, Either):

    _lifted_methods_ = tensor_methods

class Backend(WrapRing):
    
    _api_ : Interface

    @classmethod
    def new(cls, A:type|Interface=None):
        api = cls._api_ 
        if A is None:
            A = api.Array
        Wrap_A = super().new(A)
        Wrap_A._backend_ = cls
        Wrap_A._module_ = api.module
        # backend-specific constructor 
        Wrap_A.cast_data = api.asarray
        # dtype casts
        for dtype in api.dtypes:
            alias = dtype.split(":")[-1]
            cast = getattr(api.module, alias)
            method = lambda x: x.__class__(cast(x.data))
            setattr(Wrap_A, dtype, method)
        return Wrap_A

#====== Interfaces ======

@struct
class NumpyAPI(Interface):
    
    module = np 

    Array = np.ndarray
    asarray = np.asarray

    dtypes = [
        "float:float32",
        "double:float64",
        "int:int32",
        "long:int64",
        "cfloat",
    ]

print(NumpyAPI._values_)

@struct
class JaxAPI(Interface):

    module = jax.numpy
    Array = jax.lib.xla_extension.ArrayImpl
    asarray = jax.numpy.asarray

    dtypes = NumpyAPI().dtypes[:-1] + [
        "cfloat:complex64",
        "cdouble:complex128",
    ]


@struct
class TorchAPI(Interface):
    
    module = torch 

    Array = torch.Tensor
    asarray = torch.as_tensor

    # dtypes
    dtypes = [
        "float",
        "double",
        "int",
        "long", 
        "cfloat",
    ]

    repeat = "repeat_interleave"
    tile = "repeat"


class Backend(Stateful(Interface, default)):
    
    @classmethod
    def read_env(cls) -> str:
        env = "FP_BACKEND"
        s0 = os.environ[env] if env in os.environ else "torch"
