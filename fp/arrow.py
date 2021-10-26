from .meta import Bifunctor, Type

class Arrow(Bifunctor):
    
    def __new__(cls, A, B):

        class TAB (Type):
            
            src = A
            tgt = B 

            def __init__(self, f):
                self.__name__ = f.__name__ if f.__name__ else "\u03bb"
                self.call = f

            def __repr__(self):
                return self.__name__

            def __call__(self, x):
                """ Function application with type checks. """
                if not isinstance(x, self.src):
                    try: 
                        x = self.src(x)
                    except: 
                        raise TypeError(
                            f"Input of type {type(x)} " + \
                            f"not castable to {self.src}")

                y = self.call(x)
                if isinstance(y, self.tgt):
                    return y
                try: 
                    y = self.tgt(y)
                except:
                    raise TypeError(
                        f"Output of type {type(y)} " + \
                        f"not castable to {self.tgt}")
                return y

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
