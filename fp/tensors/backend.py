import typing

from fp.cartesian import Type, Hom, Prod, Either
from fp.instances import Lift, Wrap, Alg, Ring, Stateful
from fp.instances import struct

from .interfaces import Interface, INTERFACES, StatefulInterface


@struct
class LiftWrap(Lift):
    """Lifts a method to the wrapper type."""

    from_source = lambda x: x.data


TENSOR_METHODS = [
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

    The `Backend` type constructor also takes care of setting the `_inteface_`
    reference meant to be used by the downstream `TensorBase` mixin class.
    The metaclass factory logic is localised here, while `TensorBase`
    provides the rest of the API in a more readable and pythonic way.
    """

    _lifted_methods_ = TENSOR_METHODS

    @classmethod
    def new(cls, api: Interface):
        # allow overriding of `api.Array` with Union for mocked api
        Array = cls._Array_ if hasattr(cls, "_Array_") else api.Array
        B = super(cls, cls).new(Array)
        B._Array_ = Array
        B._interface_ = api
        return B

    @classmethod
    def _get_Array_(cls, api: Interface) -> type:
        """Read `api.Array` attribute, to allow overrides."""
        return api.Array

    def _post_new_(B, api: Interface):
        """Initialize wrapper type with interface fields."""
        # call Wrap._post_new_, lifting algebraic methods
        super()._post_new_(B._Array_)
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
