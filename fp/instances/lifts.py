from .struct import struct
from fp.cartesian import Type, Hom, Either

import typing


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

    For general signatures `(A, ...) -> A`, the `from_source` projection will only be
    applied to the arguments enumerated by the `lift_args` parameter, which defaults to
    `...` and can be given as `tuple[int, ...]` otherwise.

    When `lift_args` is `...` (the default), the method `name : (A, ...) -> A` only has
    arguments in `A` and its signature can be given as an int (its _arity_), e.g.

        class MyMonoid:
            __add__ = Lift(2)

    Otherwise, because the method's signature is meant to depend on `A`, it is expected to
    be given as a `type -> Hom` callable:

        class MyArray:
            reshape = Lift(lambda T: Hom((T, tuple), T), lift_args=(0,))


    Parameters
    ----------
    signature : int | Callable[type, Hom]
        number of arguments when `lift_args = ...` or callable signature
    from_source : Callable[type, type]
        extracts input values specified by `lift_args` before applying
        the wrapped method.
    to_target : Callable[type, type]
        lift returned value back to wrapping type
    lift_args : ... | int | tuple[int, ...]
        arguments to be projected onto original type:
        all (`...`), one (`int`) or only a selection (`tuple`).
    name : str | None
        managed by `__set_attr__`
    """

    signature: Either(int, typing.Callable)
    # override default lift for each functor
    from_source: typing.Callable = lambda x: x
    to_target: typing.Callable = lambda y: y
    #
    lift_args: Either(type(...), int, tuple) = ...
    flip: int = 0
    # manage by __set_name__
    name: typing.Optional[str] = None

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self.hom(objtype)
        else:
            method = self.hom(type(obj))
            return method(obj)

    def __set_name__(self, objtype, name):
        self.name = name

    def homtype(self, objtype: type) -> Hom:
        """
        Parse method signature specified on `objtype`.
        """
        if callable(self.signature.data):
            hom = self.signature.data(objtype)
            return Hom(hom.src, hom.tgt)
        elif type(self.signature.data) is int:
            n = self.signature.data
            return Hom(tuple([objtype] * n), objtype)
        else:
            print("homtype", type(self.signature), objtype)

    def method(self):
        return LiftedMethod(self)

    def hom(self, objtype: type) -> Hom.Object:
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
