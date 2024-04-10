from fp.meta import Type, FunctorClass, Hom 


class Id(metaclass=FunctorClass):

    def __new__(cls, A):
        if isinstance(A, Type):
            return A

        class IdA(A, Type):
            pass

        return IdA

    @classmethod
    def fmap(cls, f):
        src, tgt = cls(f.src), cls(f.tgt)
        return Hom(src, tgt)(f)

    @classmethod
    def name(cls, A):
        return A.__name__.capitalize()


class List(metaclass=FunctorClass):
    
    @classmethod
    def new(cls, A):

        class List_A(list, Type):

            def __init__(self, xs):
                iterable = "__iter__" in dir(xs)
                if iterable:
                    allA = 0 == sum((not isinstance(x, A) for x in xs))
                    if allA:
                        return super().__init__(xs)
                    if "cast" in dir(A):
                        try:
                            return super().__init__([A.cast(x) for x in xs])
                        except:
                            pass
                raise TypeError(
                    f"Could not cast {type(xs).__name__} "
                    + f"to {self.__class__.__name__}"
                )

            @classmethod
            def cast(cls, xs):
                return cls(xs)

            def __repr__(self):
                return "[" + ", ".join([str(x) for x in self]) + "]"

        return List_A
    
    def __init__(LA, A):
        ...

    @classmethod
    def fmap(cls, f):
        """List map: (A -> B) -> List A -> List B"""

        #@Hom(cls(f.src), cls(f.tgt))
        def mapf(xs):
            return [f(x) for x in xs]

        mapf.__name__ = f"map {f.__name__}"
        return mapf
