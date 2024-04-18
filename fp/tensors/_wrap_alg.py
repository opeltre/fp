import torch
import numpy as np

from fp.instances import Type, Hom, Wrap, Alg, Ring

signature = lambda n : lambda A: Hom(tuple([A] * n), A)

class WrapRing(Ring, Wrap):

    _lifted_methods_ = [
        ("__add__", signature(2) , ...),
        ("__sub__", signature(2), ...),
        ("__mul__", signature(2), ...),
        ("__truediv__", signature(2), ...),
        ("__neg__", signature(1), ...),
    ]


class Backend(WrapRing):

    as_tensor : str

    dtypes : list[str]
    
    @classmethod
    def new(cls, A):
        Wrap_A = super().new(A)
        # backend-specific constructor 
        Wrap_A.cast_data = getattr(cls.module, cls.as_tensor)
        # dtype casts
        for dtype in cls.dtypes:
            alias = dtype.split(":")[-1]
            cast = getattr(cls.module, alias)
            method = lambda x: x.__class__(cast(x.data))
            setattr(Wrap_A, dtype, method)
        return Wrap_A


class TorchBackend(Backend):
    
    module = torch 
    as_tensor = "as_tensor"

    dtypes = [
        "float",
        "double",
        "int",
        "long", 
        "cfloat",
    ]


class NumpyBackend(Backend):
    
    module = np 
    as_tensor = "asarray"

    dtypes = [
        "float:float32",
        "double:float64",
        "int:int32",
        "long:int64",
        "cfloat",
    ]

class JaxBackend(NumpyBackend):
    ...
