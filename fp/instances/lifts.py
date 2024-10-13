from .struct import struct
from fp.cartesian import Type, Hom, Either

import typing
from types import FunctionType


@struct
class Lift:
    """
    Declarative definition of method lifts.

    Given a type constructor or functor `T`, and assuming types `A` of a given
    type class `C` carry a method `name : (A, ...) -> A`, lifts take care of
    assigning a method `name` on the transformed type.

    The `struct` fields of a `Lift` instance describe the name and
    signature of the method to be lifted, as well as the two interlacing
    maps `from_source` and `to_target`, which in the simplest case (`signature = 1`)
    allow completion of the diagram:

                        T A ---> T A
                         .        ^
        from_source      .        '     to_target
                         v        '
                         A  --->  A

    When the method `name : (A, ...) -> `A` has multiple arguments, they can be assumed
    all in `A` by providing an `int` as signature argument. Otherwise, the signature should
    be a callable mapping `A : type` to the lifted method's signature, i.e. its
    `Hom` type instance.

    Parameters
    ----------
    name : str
    signature : int | Callable
        number of same-type arguments, or callable signature `type -> Hom`
    lift_args : ... | int | tuple[int, ...]
        arguments to be projected onto original type:
        all (`...`), one (`int`) or only a selection (`tuple`).
    from_source : Callable
    to_target : Callable
    """

    name: str
    signature: Either(int, typing.Callable)
    lift_args: Either(type(...), int, tuple) = ...
    flip: int = 0
    # override default lift for each functor
    from_source: typing.Callable = lambda x: x
    to_target: typing.Callable = lambda x: x

    def homtype(self, objtype: type) -> Hom:
        """
        Parse method signature specified on `objtype`.
        """
        if callable(self.signature.data):
            hom = self.signature.data(objtype)
            return HomLift(hom.src, hom.tgt)
        elif type(self.signature.data) is int:
            n = self.signature.data
            return HomLift(tuple([objtype] * n), objtype)
        else:
            print("homtype", type(self.signature), objtype)

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
        lifted = homtype(self.raw_lift(objtype, lift_args))
        lifted.__name__ = self.name
        return lifted

    def raw_lift(self, objtype: type, lift_args: tuple[int, ...]) -> typing.Callable:
        """
        Lifted callable S' -> T' to be hom-typed.
        """
        method = self.raw(objtype)
        m = max(lift_args)
        from_source = [1] * (m + 1)
        for i in lift_args:
            from_source[i] = self.from_source

        def lifted(*xs):
            head = (x if f == 1 else f(x) for x, f in zip(xs, from_source))
            tail = (x for x in xs[m + 1 :])
            y = self.to_target(method(*head, *tail))
            return y

        return lifted

    def raw(self, objtype: type) -> typing.Callable:
        """Callable S -> T to be lifted."""

        def raw_bound_method(x, *xs):
            return getattr(x, self.name)(*xs)

        return raw_bound_method


@struct
class WrapLift(Lift):
    from_source = lambda x: x.data


@struct
class ProdLift(Lift):
    from_source = lambda x: x[0]


class HomLift(Hom):

    class Object(Hom.Object):

        def __get__(self, obj, objtype=None):
            if obj is not None:
                return Hom.partial(self, obj)
            else:
                return self


class LiftedMethod:

    def __init__(self, lift: Lift):
        self.lift = lift
        if isinstance(lift.signature, int):
            r = lift.signature
            self.signature = lambda T: Hom(tuple([T] * r), T)
        else:
            self.signature = signature

    def method(self, obj: typing.Any) -> Type.Hom.Object:
        """
        Lift a method to the wrapped type.
        """
        lift_args = self.lift.lift_args
        homtype = self.lift.signature(type(obj))
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
            return io.cast(method(*xs), homtype.tgt)

    def __set_name__(self, name, objtype):
        self.lifted = getattr(objtype._lifted_, self.name)
        try:
            homtype = self.signature(objtype)
            self.typed = homtype(self.lifted)
        except:
            print("invalid signature")
            self.typed = self.lifted
        # unused
        self.target_name = name

    def __get__(self, obj, objtype=None):
        if obj is not None:
            return self.typed(obj)
        else:
            return self.typed

    def __set__(self, obj, val): ...

    def __getattr__(self, attr):
        try:
            return super().__getattr__(attr)
        except AttributeError:
            return getattr(self.lift, attr)
