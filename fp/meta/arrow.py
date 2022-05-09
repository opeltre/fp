from .functor import Bifunctor
from .type    import Type, TypeMeta
from .cartesian import Prod

class Arrow(Bifunctor):
    
    def __new__(cls, A, B):

        class TAB (Type):
            
            if isinstance(A, type):
                src, tgt, arity = (A, B, 1)
            elif '__iter__' in dir(A):
                As = Prod(*A)
                src, tgt, arity = (As, B, len(As.types))
            else:
                raise TypeError(
                    f"Source {A} is not a type nor an iterable of types")
    
            def __init__(self, f):
                self.__name__ = f.__name__ if f.__name__ else "\u03bb"
                self.call = f

            def __repr__(self):
                return self.__name__

            def __call__(self, *xs):
                """ Function application with type checks and curryfication. """
                
                #--- Arity check
                if len(xs) == self.arity:
                    src = self.src
                elif len(xs) < self.arity:
                    t1s  = self.src.types[:len(xs)]
                    src = Prod(*t1s)
                else: 
                    raise TypeError(
                        f"{self.arity}-ary function called with " + \
                        f"{len(xs)} arguments")
               
                #--- Input type check
                try:
                    Tx = src.cast(*xs)
                except: 
                    input = " * ".join([str(type(x)) for x in xs])
                    raise TypeError(
                        f"Input of type {input} " + \
                        f"not castable to {self.src}")
                
                #--- Curried section 
                if len(xs) < self.arity:
                    t2s  = self.src.types[-(self.arity-len(xs)):] 
                    src2 = tuple(t2s) if len(t2s) > 1 else t2s[0] 

                    @Arrow(src2, self.tgt)
                    def curried(*ys): 
                        return self(*xs, *ys)
                    
                    curried.__name__ = (f'{self.__name__} '
                                     + ' '.join((str(x) for x in Tx)))
                    return curried

                #--- Unary call 
                if len(xs) == 1 and self.arity == 1:
                    y = self.call(Tx)
                #--- N-ary call (Tx :: Prod)
                elif len(xs) == self.arity:
                    y = self.call(*Tx)
                
                #--- Cast output 
                try: 
                    Ty = self.tgt.cast(y)
                    return Ty
                except: 
                    raise TypeError(
                        f"Output of type {type(y)} " + \
                        f"not castable to {self.tgt}")

            def __matmul__(self, other):
                """ Composition of functions. """
                if not self.src == other.tgt:
                    raise TypeError(f"Uncomposable pair"\
                            + f"{(self.src, self.tgt)} @"\
                            + f"{(other.src, other.tgt)}")
                src, tgt = other.src, self.tgt
                comp = lambda *xs: self(other(*xs))
                comp.__name__ = f"{self.__name__} . {other.__name__}"
                return Arrow(src, tgt)(comp)

        return TAB

    @classmethod
    def name(cls, A, B):
        if isinstance(A, type):
            return f"{A.__name__} -> {B.__name__}" 
        input = " -> ".join([Ak.__name__ for Ak in A])
        return f"{input} -> {B.__name__}"