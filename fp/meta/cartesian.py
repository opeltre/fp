from .functor   import FunctorMeta
from .type      import Type

class NFunctorMeta(FunctorMeta):
    
    kind  = "(*, ...) -> *"
    arity = 'n'


class Prod(metaclass=NFunctorMeta):

    def __new__(cls, *As):

        class Prod_As(Type):
            
            types = As

            def __init__(self, *xs):
                self.elems = [A.cast(x) for A, x in zip(self.types, xs)]

            def __repr__(self):
                return "(" + ", ".join([str(x) for x in self.elems]) + ")"
                
        return Prod_As

    @classmethod
    def name(cls, *As):
        names = [A.__name__ for A in As]
        return f"({', '.join(names)})"