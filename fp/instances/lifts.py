from .struct import struct
from fp.cartesian import Type, Hom, Either

import typing
from types import FunctionType

@struct
class Lift:
    """
    Declarative definition of method lifts.
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
        Return the lifted callable to be wrapped.
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
                return Hom.curry(self, (obj,))
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
    
    def method(self, obj: typing.Any) -> Type.Hom.Object :
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

    def __get__(self, obj, objtype =None):
        if obj is not None:
            return self.typed(obj)
        else: 
            return self.typed

    def __set__(self , obj, val):
        ...

    def __getattr__(self, attr):
        try:
            return super().__getattr__(attr)
        except AttributeError:
            return getattr(self.lift, attr)
