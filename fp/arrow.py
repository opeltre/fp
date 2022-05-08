from .meta      import Bifunctor, Type, Prod

class Arrow(Bifunctor):
    
    def __new__(cls, A, B):

        class TAB (Type):
            
            if isinstance(A, type):
                src, tgt, arity = (A, B, 1)
            elif '__iter__' in dir(A):
                As = Prod(*A)
                src, tgt, arity = (As, B, len(As))
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
                print(self.arity - len(xs))

                if len(xs) == self.arity:
                    src = self.src
                elif len(xs) < self.arity:
                    src = self.src[:len(xs)]
                else: 
                    raise TypeError(
                        f"{self.arity}-ary function called" + \
                        f"{len(xs)} arguments")
                #--- Input type check
                try:
                    Tx = src.cast(*xs)
                except: 
                    input = " * ".join([str(type(x)) for x in xs])
                    raise TypeError(
                        f"Input of type {input} " + \
                        f"not castable to {src}")
                
                #--- Curried section 
                if len(xs) < self.arity:
                    src2 = src[-(self.arity-len(xs)):]
                    @Arrow(src2, tgt)
                    def curried(*ys): return self.call(*xs, *ys)
                    return curried

                #--- Unary call 
                if self.arity == 1 and len(xs) == 1:
                    y = self.call(Tx)
                #--- N-ary call (Tx :: Prod)
                elif self.arity == len(xs):
                    y = self.call(*Tx)
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
                return Arr(src, tgt)(comp)

        return TAB

    @classmethod
    def name(cls, A, B):
        return f"{A.__name__} -> {B.__name__}"
