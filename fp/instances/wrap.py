from fp.meta import Type, Functor, Functor
from fp.cartesian import Hom, Prod
from fp.meta.lifts import Lift as LiftBase
import fp.utils as utils

from types import MethodType
from typing import Callable, Iterable


class WrapObject(Functor.TopType, metaclass=Type):
    """
    Base type for wrapped values.
    """

    _wrapped_: Type

    def __init__(self, data):
        """Wrap a value."""
        A = self._wrapped_
        if isinstance(data, A):
            self.data = data
        elif "cast_data" in dir(self.__class__):
            self.data = self.__class__.cast_data(data)
        else:
            try:
                self.data = A(data)
            except:
                raise utils.TypeError("input for Wrap {A}", data, A)

    def __repr__(self):
        return self._wrapped_.__str__(self.data)

    @classmethod
    def cast(cls, data):
        if isinstance(data, cls):
            return data
        T = type(data)
        if "_head_" in dir(T) and "data" in dir(data):
            return cls(data.data)
        return cls(data)

    def __init_subclass__(child, **kws):
        cls = super(child, child)
        msg = str(cls._head_) + " __init_subclass__: " + child.__name__
        utils.log(msg, v=1)


class Wrap(Type, metaclass=Functor):
    """
    Type wrappers hoding a `.data` attribute.
    """

    Object = WrapObject

    class Lift(LiftBase):

        @staticmethod
        def from_source(x):
            return x.data

        @staticmethod
        def to_target(x):
            return x

    @classmethod
    def new(cls, A):
        Wrap_A = super().new(A)
        Wrap_A._wrapped_ = A
        return Wrap_A

    @classmethod
    def _subclass_(cls, *As):
        msg = str(cls) + " _subclass_: "
        msg += " ".join(str(A) for A in As[:2])
        utils.log(msg, v=1)
        return Type.__new__(cls, *As)

    @classmethod
    def join(cls, wwx):
        A = wwx._tail_[0]._tail_[0]
        return cls(A)(x.data.data)

    @classmethod
    def unit(cls, x):
        return cls(type(x))(x)

    @classmethod
    def lift(
        cls,
        method: MethodType,
        homtype: Type,
        lift_args: Iterable[int] | type(...) = ...,
    ) -> Type.Hom.Object:
        """
        Lift a method to the wrapped type.
        """
        if isinstance(lift_args, int):
            lift_args = (lift_args,)
        elif lift_args is ...:
            lift_args = tuple(range(homtype.arity))

        @homtype
        def lifted_method(*xs):
            """
            Lifted method.
            """
            xs = list(xs)
            for i in lift_args:
                xs[i] = xs[i].data
            return utils.cast(method(*xs), homtype.tgt)

        lifted_method.__name__ = method.__name__
        return lifted_method

    @classmethod
    def fmap(cls, f):
        @Hom(f.src, f.tgt)
        def wrap_f(x):
            return f(x.data)

        wrap_f.__name__ = "Wrap " + f.__name__
        return wrap_f

    @classmethod
    def fmap2(cls, f):
        map_f = lambda x, y: f(x.data, y.data)
        map_f.__name__ = f"map2 {f.__name__}"
        return map_f

    @classmethod
    def fmapN(cls, f):
        src = tuple([cls(si) for si in f.src._tail])
        tgt = cls(f.tgt)
        map_f = Type.Hom(src, tgt)(lambda *xs: f(*(x.data for x in xs)))
        map_f.__name__ = f"mapN {f.__name__}"
        return map_f
