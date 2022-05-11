from .type      import Type, TypeMeta
from .functor   import BifunctorMeta, NFunctorMeta


class ArrowMeta(BifunctorMeta):

    def __new__(cls, name, bases, dct):
        Arr = super().__new__(cls, name, bases, dct)
        Arr.curry = cls.curry_method(Arr)
        if not '__matmul__' in dir(Arr):
            Arr.__matmul__ = cls.matmul_method(Arr)
        return Arr
    
    @staticmethod
    def source(Arr, xs):
        """ 
        Source type and cast result of n-ary input xs for n <= arity. 
        """
        #--- Arity check
        if len(xs) == Arr.arity:
            src = Arr.src
        elif len(xs) < Arr.arity:
            ts  = Arr.src.types[:len(xs)]
            src = Prod(*ts)
        else: 
            raise TypeError(
                f"{Arr.arity}-ary function called with " + \
                f"{len(xs)} arguments")
        try:
            Tx = src.cast(*xs)
        except: 
            input = "(" + ", ".join([str(type(x)) for x in xs]) + ")"
            raise TypeError(
                f"Input of type {input} " + \
                f"not castable to {Arr.src}")
        return src, Tx

    @staticmethod
    def target(arr, y):
        """ Cast of output y. """
        if isinstance(y, arr.tgt):
            return y
        try: 
            Ty = arr.tgt.cast(y)
            return Ty
        except: 
            raise TypeError(
                f"Output of type {type(y)} " + \
                f"not castable to {arr.tgt}")

    @staticmethod
    def curry_method(Arr):

        def curry(f, xs):
            """ 
            Curried function applied to n-ary input xs for n < arity. 
            """
            if len(xs) < f.arity:
                ts  = f.src.types[-(f.arity-len(xs)):] 
                src = tuple(ts) if len(ts) > 1 else ts[0] 
                
                @Arr(src, f.tgt)
                def curried(*ys): 
                    return f(*xs, *ys)
                
                curried.__name__ = (f'{f.__name__} '
                                    + ' '.join((str(x) for x in xs)))
                return curried

            raise TypeError(
                    f"Cannot curry {Arr.arity} function on " +\
                    f"{len(xs)}-ary input")

        return curry

    @classmethod
    def call_method(cls, Arr):
        
        def _call_(arrow, *xs):
            """ 
            Function application with type checks and curryfication. 
            """
            f = arrow.call
            #--- Input type check
            src, Tx = cls.source(arrow, xs)           
            #--- Unary and N-ary call
            if len(xs) == arrow.arity:
                y = f(Tx) if len(xs) == 1 else f(*Tx)
                return cls.target(arrow, y)
            #--- Curried section 
            if len(xs) < arrow.arity:
                return Arr.curry(arrow, xs)

        return _call_

    @classmethod
    def matmul_method(cls, Arr):
        """ Composition of functions. """
        def _matmul_(self, other):
            if not self.src == other.tgt:
                raise TypeError(f"Uncomposable pair"\
                        + f"{(self.src, self.tgt)} @"\
                        + f"{(other.src, other.tgt)}")
            src, tgt = other.src, self.tgt
            comp = lambda *xs: self(other(*xs))
            comp.__name__ = f"{self.__name__} . {other.__name__}"
            return Arr(src, tgt)(comp)
        return _matmul_


class Prod(metaclass=NFunctorMeta):

    def __new__(cls, *As):

        class Prod_As(tuple, metaclass=TypeMeta):

            types = As

            def __new__(cls, *xs):
                if len(xs) != len(cls.types):
                    raise TypeError( 
                        f"Invalid number of terms {len(xs)} " +\
                        f"for {len(cls.types)}-ary product.")
                def cast(A, x): 
                    return x if isinstance(x, A) else A.cast(x)
                elems = [cast(A, x) for A, x in zip(cls.types, xs)]
                return super().__new__(cls, elems)
            
            def __init__(self, *xs):
                pass 

            def __repr__(self):
                return "(" + ", ".join([str(x) for x in self]) + ")"

            @classmethod
            def cast(cls, *xs):
                return cls(*xs)
                
        return Prod_As
    
    def __init__(self, *As):
        pass
        
    @classmethod
    def fmap(cls, *fs):
        
        src = cls((f.src for f in fs))
        tgt = cls((f.tgt for f in fs))

        @Arrow(src, tgt)
        def map_f(*xs):
            return tgt(*(f(x) for x, f in zip(xs, fs)))

        map_f.__name__ = "(" + ", ".join((f.__name__ for f in fs)) + ")"
        return map_f

    @classmethod
    def name(cls, *As):
        names = [A.__name__ for A in As]
        return f"({', '.join(names)})"  


class Arrow(metaclass=ArrowMeta):
    
    def __new__(cls, A, B):

        class TAB (Type):

            functor = Arrow
            input   = (A, B)
            
            if isinstance(A, type):
                src, tgt, arity = (A, B, 1)
            elif '__iter__' in dir(A):
                As = Prod(*A)
                src, tgt, arity = (As, B, len(As.types))
            else:
                raise TypeError(
                    f"Source {A} is not a type nor an iterable of types")
    
            def __init__(self, f):
                if not callable(f):
                    raise TypeError(f"Input is not callable.")
                self.call = f
                self.__name__ = f.__name__ if f.__name__ else "\u03bb"

            def __repr__(self):
                return self.__name__

        TAB.__call__   = cls.call_method(Arrow)
        TAB.__matmul__ = cls.matmul_method(Arrow)

        return TAB

    def __init__(self, A, B):
        pass

    @classmethod
    def name(cls, A, B):
        if isinstance(A, type):
            return f"{A.__name__} -> {B.__name__}" 
        input = " -> ".join([Ak.__name__ for Ak in A])
        return f"{input} -> {B.__name__}"
