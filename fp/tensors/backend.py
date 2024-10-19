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

    The
    """

    _interface_: Interface
    _lifted_methods_ = TENSOR_METHODS

    @classmethod
    def new(cls, api: Interface):
        B = super(cls, cls).new(api.Array)
        B._interface_ = api
        return B

    def _post_new_(B, api: Interface):
        """Initialize wrapper type with interface fields."""
        # call Wrap._post_new_, lifting algebraic methods
        super()._post_new_(api.Array)
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


class StatefulBackend(Backend):

    Array = typing.Union[*(api.Array for api in INTERFACES.values())]

    @classmethod
    def new(cls, api: StatefulInterface):
        B = super(Backend, cls).new(cls.Array)
        B._interface_ = api.mock("state")
        B._stateful_ = type(api)
        return B

    def _post_new_(B, api: StatefulInterface):
        """Initialize wrapper type with interface fields."""
        # call Wrap._post_new_, lifting algebraic methods
        super(Backend, B)._post_new_(B.Array)

        # backend-specific constructor
        B.cast_data = lambda x: B._interface_.asarray(x)

        B.__repr__ = lambda x: str(x.data)

        #   B.cast_data = api.asarray
        #   # dtype casts
        #   for dtype in api.dtypes:
        #       alias = dtype.split(":")[-1]
        #       cast = getattr(api.module, alias)
        #       method = lambda x: x.__class__(cast(x.data))
        #       setattr(B, dtype, method)
        return B
