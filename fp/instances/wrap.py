from fp.meta import Type, Monad
from .hom import Hom
import fp.io as io

from types import MethodType
from typing import Callable, Iterable


class WrappedType(Monad._instance_, metaclass=Type):
    """
    Base type for wrapped values.
    """
    _wrapped_ : Type

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
                raise io.TypeError("input for Wrap {A}", data, A)

    def __repr__(self):
        return self._tail_[0].__str__(self.data)
    
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
        try:
            type(child)._post_new_(child, cls._wrapped_)
        except:
            ...



class Wrap(Type, metaclass=Monad):
    """
    Type wrapper lifting selected methods to the container type.

    The class method `lift` will iterate over the class attribute 
    `_lifted_methods_` to assign lifted methods on the wrapped type.
    
    Attributes:
    -----------
        _lifted_methods_ (`list`): 
            A list of of triples `(name, signature, lift_args)` where
                * name (`str`): name of the method to be lifted,
                * signature (`Callable[type, Type]`) yielding lifted method type `signature(cls)`,
                * lift_args (`int | tuple[int] | type(...)`) index of arguments to be unwrapped.
            
            **Example**

            .. code::
            
                class StrWrapper(Wrap):

                    _lifted_methods_ = [
                        ('upper', lambda A: Hom(A, A), ...)
                        ('isalnum', lambda A: Hom(A, Bool), ...)
                        ('join', lambda A: Hom((A, List[A]), Bool), 0)
                    ]
    """

    _top_ = WrappedType
    
    _lifted_methods_ = []
    
    @classmethod
    def new(cls, A):
        Wrap_A = super().new(cls, A)
        Wrap_A._wrapped_ = A
        return Wrap_A

    def _post_new_(Wrap_A, A):
        # --- Lift methods
        Wrap_A.lifts = {}
        cls = Wrap_A.__class__
        for name, signature, lift_args in cls._lifted_methods_:
            homtype = signature(Wrap_A)
            f = getattr(A, name)
            Wf = cls.lift(f, homtype, lift_args)
            setattr(Wrap_A, name, Wf)
            Wrap_A.lifts[name] = Wf
        return Wrap_A

    def __init__(Wrap_A, *As):
        ...

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
    ) -> Type.Hom._top_ :
        """
        Lift a method to the wrapped type. 
        """
        if isinstance(lift_args, int):
            lift_args = (lift_args,)
        elif lift_args is ...:
            lift_args = tuple(range(homtype.arity))

        @homtype
        def lifted_method(*xs):
            xs = list(xs)
            for i in lift_args:
                xs[i] = xs[i].data
            return io.cast(method(*xs), homtype.tgt)
        
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
