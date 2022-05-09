from .functor   import FunctorMeta
from .type      import Type

class NFunctorMeta(FunctorMeta):
    
    kind  = "(*, ...) -> *"
    arity = 'n'


class Prod(metaclass=NFunctorMeta):

    def __new__(cls, *As):

        class Prod_As(tuple, Type):

            types = As

            def __new__(cls, *xs):
                if len(xs) != len(cls.types):
                    raise TypeError( 
                        f"Invalid number of terms {len(xs)} " +\
                        f"for {len(cls.types)}-ary product.")
                elems = [A.cast(v) for A, v in zip(cls.types, xs)]
                return super().__new__(cls, elems)
            """
            def __init__(self, *xs):
                if len(xs) != len(self.types):
                    raise TypeError( 
                        f"Invalid number of terms {len(xs)} " +\
                        f"for {len(cls.types)}-ary product.")
                self.elems = [A.cast(x) for A, x in zip(self.types, xs)]

                for name in ["iter", "getitem", "setitem"]:
                    method = getattr(self.elems, f"__{name}__")
                    setattr(self, "__{name}__", method)
            """      

            def __repr__(self):
                return "(" + ", ".join([str(x) for x in self]) + ")"

            @classmethod
            def cast(cls, *xs):
                return cls(*xs)
                
        return Prod_As 

    @classmethod
    def name(cls, *As):
        names = [A.__name__ for A in As]
        return f"({', '.join(names)})"  