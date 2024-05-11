import torch
import jax
import numpy as np

from types import ModuleType
from typing import Callable

from fp.cartesian import Type, Hom, Prod, Either
from fp.instances import Lift, Wrap, Alg, Ring, Stateful
from fp.instances import struct, List, Str

import os

signature = lambda n : lambda A: Hom(tuple([A] * n), A)

@struct
class LiftWrap(Lift):
    from_source = lambda x: x.data

tensor_methods = [
    # reshapes
    LiftWrap("__add__", 2),
    LiftWrap("__sub__", 2),
    LiftWrap("__mul__", 2),
    LiftWrap("__truediv__", 2),
    LiftWrap("__neg__", 1),
    # reshapes
    LiftWrap("flatten", 1),
    LiftWrap("reshape", lambda T: Hom((T, tuple), T), 0, flip=1),
]

class WrapRing(Ring, Wrap):

    _lifted_methods_ = tensor_methods

#====== Interfaces ======

@struct
class Interface:
    module : ModuleType
    Array : type
    asarray : Callable
    dtypes : List(Str)
    # aliases
    repeat : Str = "repeat"
    tile : Str = "tile"
    
    def __repr__(self):
        return self.module.__name__

    def __str__(self):
        return self.module.__name__

@struct
class LiftInterface(LiftWrap):
    
    def raw(self, objtype:type) -> Callable:
        method = getattr(objtype.Array, self.name)
        return method

#====== Backend: Wrap an interface ======

class Backend(Ring, Wrap):
    
    _api_ : Interface
    _lifted_methods_ = [LiftInterface(**lift) for lift in tensor_methods]
    
    @classmethod
    def new(cls, api:Interface):
        B = super(cls, cls).new(api.Array)
        B._backend_ = api
        return B

    def _post_new_(B, api:Interface):
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
        B = super()._subclass_(name, bases, dct)
        B._wrapped_ = bases[0]._wrapped_
        type(B)._post_new_(B, bases[0]._backend_)
        return B

class EitherRing(Ring, Either):

    _lifted_methods_ = tensor_methods

class StatefulEither(Either):

    class Object(Either.Object):
        
        state: type
        _lifts_: list[str] = []

    def _post_new_(E, *As):
        super()._post_new_(*As)
        if not hasattr(E, "state"):
            E.state = E._tail_[0]
        E.use(E.state)

    @classmethod
    def _subclass_(cls, name, bases, dct):
        dct = dct | {"state": bases[0].state}
        E = super()._subclass_(name, bases, dct)
        return E

    def use(E, state):
        E.state = state
        for name in E._lifts_:
            setattr(E, name, getattr(E.state, name))
    
