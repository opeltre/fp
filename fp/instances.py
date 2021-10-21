from .meta  import Type, Functor
from .arrow import Arrow

class Id (Functor):
    
    def __new__(cls, A):
        if isinstance(A, Type):
            return A
        
        class IdA (A, Type):
            pass

        return IdA
    
    def __init__(TA, A):
        TA.functor.types[A]  = TA
        TA.functor.types[TA] = TA

    @classmethod
    def fmap(cls, f):
        src, tgt = cls(f.src), cls(f.tgt)
        return Arrow([src, tgt], f)

    @classmethod
    def name(cls, A):
        return A.__name__.capitalize()

class List(Functor):

    def __new__(cls, A):

        class List_A(list, Type):

            def __init__(self, xs):
                iterable = "__iter__" in xs.__dir__()
                if iterable: 
                    allA = (0 == sum((not isinstance(x, A) for x in xs)))
                    if allA:
                        return super().__init__(xs)
                    try: 
                        return super().__init__([A(x) for x in xs])
                    except:
                        pass
                raise TypeError(
                    f"Could not cast {type(xs).__name__} " +\
                    f"to {self.__class__.__name__}")
            
        return List_A

    @classmethod
    def fmap(cls, f):
        """ List map: (A -> B) -> List A -> List B """
        src, tgt = cls(f.src), cls(f.tgt)
        def mapf(xs):
            if not isinstance(xs, src):
                raise TypeError(f"Input not of type {src}")
            return tgt([f(x) for x in xs])
        return Arrow([src, tgt], mapf)
