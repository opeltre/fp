import typing
import functools

from fp.cartesian import Type, Hom, Prod, Either
from fp.instances import Lift, Wrap, Alg, Ring, Stateful
from fp.instances import struct

from .interfaces import Interface, INTERFACES, StatefulInterface


@struct
class LiftWrap(Lift):
    """Lifts a method to the wrapper type."""

    from_source = lambda x: x.data


TENSOR_METHODS = [
    #   # arithmetic methods
    #   LiftWrap("__add__", 2),
    #   LiftWrap("__sub__", 2),
    #   LiftWrap("__mul__", 2),
    #   LiftWrap("__truediv__", 2),
    #   LiftWrap("__neg__", 1),
    #   # reshapes
    #   LiftWrap("flatten", 1),
    #   LiftWrap("reshape", lambda T: Hom((T, tuple), T), 0, flip=1),
]

# ====== Backend: Wrap an interface ======


class Backend(Ring, Wrap):
    """Functor wrapping the `Array` type of an `Interface` object.

    Any value `array : Backend(interface)` holds an object `array.data`
    that is an instance of the plain python type `interface.Array`.

    This class inherits from `Ring` and `Wrap` as a type constructor, which
    have the following effects:

    * `Wrap` maps the `interface.Array` type to a `Backend` type instance
      and lifts algebraic operators `__add__`, etc. to the wrapper type,
    * `Ring` then binds typed algebraic classmethods such i.e. `add`, ...
      to the `Backend` type.

    The `Backend` class is also meant to handle a mock of the `Interface` object,
    i.e. `StatefulInterface.mock()`.  The `StatefulInterface.use` context manager
    gives a single entry point for managing the global state.

    Note
    ----
    The `Backend` type constructor also takes care of setting the `_inteface_`
    reference meant to be used by the downstream `TensorBase` mixin class.
    The metaclass factory logic is localised here, while `TensorBase`
    provides the rest of the API in a more readable and pythonic way.
    """

    class Object(Wrap.Object):
        __add__ = LiftWrap(2)
        __sub__ = LiftWrap(2)
        __mul__ = LiftWrap(2)
        __neg__ = LiftWrap(1)
        __truediv__ = LiftWrap(2)
        flatten = LiftWrap(1)
        reshape = LiftWrap(lambda T: Hom((T, tuple), T), lift_args=0, flip=1)

    @classmethod
    def new(cls, api: Interface):
        # allow overriding of `api.Array` with Union for mocked api
        Array = cls._Array_ if hasattr(cls, "_Array_") else api.Array
        B = super(cls, cls).new(Array)
        B._Array_ = Array
        B._interface_ = api
        return B

    def _post_new_(B, api: Interface):
        """Initialize wrapper type with interface fields."""
        # call Wrap._post_new_, lifting algebraic methods
        super()._post_new_(B._Array_)
        # call backend-specific constructor lazily for mocked api
        B.cast_data = lambda x: api.asarray(x)
        # assign dtype casts
        for dtype in api.dtypes.keys():
            setattr(
                B,
                dtype,
                functools.partial(B._dtype_cast_, dtype),
            )
        return B

    def _dtype_cast_(self, dtype, x):
        cast_method = self._interface_.dtype_cast(dtype)
        return self(cast_method(x.data))

    @classmethod
    def _subclass_(cls, name, bases, dct):
        """Propagate hacky attributes to subclasses."""
        B = super()._subclass_(name, bases, dct)
        B._wrapped_ = bases[0]._wrapped_
        type(B)._post_new_(B, bases[0]._interface_)
        return B
