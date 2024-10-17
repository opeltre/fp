import torch
import jax
import numpy as np

from types import ModuleType
from typing import Callable

from fp.cartesian import Type, Hom, Prod, Either
from fp.instances import Lift, Wrap, Alg, Ring, Stateful
from fp.instances import struct, List, Str

import os


# ====== Interfaces ======


@struct
class Interface:
    """Declare bindings to a numerical backend.

    An `Interface` object can be mapped to a `TensorBase` subclass
    by a functor wrapping over the `interface.Array` type, e.g. the
    :class:`Backend` class.

    The summarized `struct` layout makes it easier to spot and enumerate what
    are mere naming differences.

    Args:
        module (ModuleType): python module
        Array (type): base array class, e.g. `np.ndarray`
        asarray (callable): default constructor
        dtypes (list[str]): list of dtypes, optionally prepended by alias + `:`, e.g.
            `"float:float32"`
        repeat (str): name of `"repeat"` method (`"repeat_interleave"` for torch)
        tile (str): name of `"tile"` method (`"repeat"` for torch)
    """

    module: ModuleType
    Array: type
    asarray: Callable
    dtypes: List(Str)
    # aliases
    repeat: Str = "repeat"
    tile: Str = "tile"

    def __repr__(self):
        return self.module.__name__

    def __str__(self):
        return self.module.__name__


@struct
class LiftWrap(Lift):
    from_source = lambda x: x.data


tensor_methods = [
    # arithmetic methods
    LiftWrap("__add__", 2),
    LiftWrap("__sub__", 2),
    LiftWrap("__mul__", 2),
    LiftWrap("__truediv__", 2),
    LiftWrap("__neg__", 1),
    # reshapes
    LiftWrap("flatten", 1),
    LiftWrap("reshape", lambda T: Hom((T, tuple), T), 0, flip=1),
]


# ====== Backend: Wrap an interface ======


class Backend(Ring, Wrap):
    """Wrap the `Array` type of an `Interface` object.

    This class inherits from `Ring` and `Wrap` as a type constructor.

    * `Wrap` maps the `interface.Array` type to a `Backend` type instance,
    * `Ring` takes care of lifting algebraic operators on `Backend` types.

    The
    """

    _interface_: Interface
    _lifted_methods_ = tensor_methods

    @classmethod
    def new(cls, api: Interface):
        B = super(cls, cls).new(api.Array)
        B._interface_ = api
        return B

    def __getattr__(self, attr: str):
        """Access interface attributes from `Backend` instance."""
        try:
            return super().__getattr__(self, attr)
        except AttributeError:
            return getattr(self._interface_, attr)

    def _post_new_(B, api: Interface):
        """Initialize wrapper type with interface fields."""
        for k, v in api.items():
            setattr(B, k, v)
        super()._post_new_(api.Array)
        B._module_ = api.module
        # backend-specific constructor
        B.cast_data = api.asarray
        # dtype casts
        for dtype in api.dtypes:
            alias = dtype.split(":")[-1]
            cast = getattr(api.module, alias)
            method = lambda x: x.__class__(cast(x.data))
            setattr(B, dtype, method)
        return B

    @classmethod
    def _subclass_(cls, name, bases, dct):
        """Propagate hacky attributes to subclasses."""
        B = super()._subclass_(name, bases, dct)
        B._wrapped_ = bases[0]._wrapped_
        type(B)._post_new_(B, bases[0]._interface_)
        return B
