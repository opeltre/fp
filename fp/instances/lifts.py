from .struct import struct
from fp.cartesian import Type, Hom

@struct
class Lift:
    name: str 
    signature: int | Callable
    lift_args: type(...) | int | tuple = ...
    flip: int = 0 
    # override default lift for each functor
    from_source : Callable = lambda x: x
    to_target : Callable = lambda x: x

@struct
class WrapLift(Lift):
    from_source = lambda x: x.data
    
@struct 
class ProdLift(Lift):
    from_source = lambda x: x[0]

class Lifted:

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
