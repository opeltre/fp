from fp import *
from fp import io
from fp.instances import struct
from fp.cartesian import Type, Hom, Either

from typing import Callable
from types import FunctionType


@struct
class Lift:
    """
    Declarative definition of method lifts.
    """

    name: Str
    signature: Either(int, FunctionType)
    lift_args: Either(type(...), int, tuple) = ...
    flip: int = 0
    # override default lift for each functor
    from_source: Callable = lambda x: x
    to_target: Callable = lambda x: x

    def homtype(self, objtype: type) -> Hom:
        """
        Parse method signature specified on `objtype`.
        """
        from_int = Hom(int, FunctionType)(lambda n: Hom(tuple([objtype] * n), objtype))
        gather = Either.gather(from_int, Hom.id(FunctionType))
        return gather(self.signature)(objtype)

    def method(self, objtype: type) -> Hom.Object:
        """
        Lift a method to the wrapped type.
        """
        # evaluate signature
        homtype = self.homtype(objtype)
        # parse lift_args
        from_dots = Hom(type(...), tuple)(lambda _: tuple(range(homtype.arity)))
        from_int = Hom(int, tuple)(lambda i: (i,))
        gather = Either.gather(from_dots, from_int, Hom.id(tuple))
        lift_args = gather(self.lift_args)
        # wrap lifted callable
        lifted = homtype(self.raw(objtype, lift_args))
        lifted.__name__ = self.name
        return lifted

    def raw(self, objtype: type, lift_args: tuple[int, ...]) -> Callable:
        """
        Return the lifted callable to be wrapped.
        """
        method = getattr(objtype, self.name)
        m = max(lift_args)
        from_source = [1] * m
        for i in lift_args:
            from_source[i] = self.from_source

        def lifted(*xs):
            head = (x if f is 1 else f(x) for x, f in zip(xs, from_source))
            tail = (x for x in xs[m + 1 :])
            y = self.to_target(method(*head, *tail))
            return y

        return lifted


@struct
class LiftEither(Lift):
    from_source = lambda x: x.data

    def raw(self, objtype: type, lift_args: tuple[int, ...]) -> Callable:

        methods = tuple(getattr(T, self.name) for T in objtype._tail_)
        m = max(lift_args)
        from_source = [1] * m
        for j in lift_args:
            from_source[j] = self.from_source

        def lifted(*xs):
            i, xs = self.promote(xs, lift_args)
            y = self.to_target(methods[i](*xs))

    def promote(self, xs: tuple, lift_args: tuple[int, ...]) -> tuple[int, tuple]:

        if lift_args == (0,):
            x = xs[0]
            return x._i_, xs

        eithers = tuple(xs[i] for i in lift_args)
        eithers_i = tuple(x._i_ for x in eithers)
        m, M = min(eithers_i), max(eithers_j)
        if m == M:
            return m, xs
        else:
            ys = list(xs)
            i = eithers_i[0]
            Ei = type(eithers[0])
            io.log("promoting Either values to first element type", v=1, prefix="/!\\")
            for l in lift_args:
                ys[l] = io.cast(ys[l], Ei)
            return i, tuple(ys)


lift = Lift("__add__", lambda T: Hom((T, T), T), ...)
liftE = LiftEither(**lift)
