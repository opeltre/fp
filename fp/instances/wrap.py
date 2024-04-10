from fp.meta import Type, FunctorClass, Hom, Prod


class Wrap(metaclass=FunctorClass):
    """
    Type wrapper lifting selected methods to the contained value.


    The `lifts` class attribute is looked up to assign lifted methods.
    It expects a dictionary of method type signatures of the following form:

        lifts = { 'name' : (homtype: Type -> Type) }

    such that `homtype(A)` is the type of method `A.name`, e.g.

        lifts = { 'add' : lambda A : Hom((A, A), A)}

    The output type `Wrap A` will inherit a method 'name' wrapping the
    call on contained values.
    """
    lifts = {} 

    @classmethod
    def new(cls, A):

        class Wrap_A(Type):

            def __init__(self, data):
                if isinstance(data, A):
                    self.data = data
                elif "cast_data" in dir(self.__class__):
                    self.data = self.__class__.cast_data(data)
                else:
                    try:
                        self.data = A(data)
                    except:
                        raise TypeError(
                            f"Received invalid input {data} : {type(data)} "
                            + f"for Wrap {A} instance"
                        )

            def __repr__(self):
                return A.__str__(self.data)

            if "__eq__" in dir(A):

                def __eq__(self, other):
                    return self.data == other.data

            @classmethod
            def cast(cls, data):
                if isinstance(data, cls):
                    return data
                T = type(data)
                if "_head" in dir(T) and "data" in dir(data):
                    return cls(data.data)
                return cls(data)

        Wrap_A.lifts = {}
        return Wrap_A


    def __init__(Wrap_A, A):
        # --- Lift methods
        cls = Wrap_A._head
        for name, homtype in cls.lifts.items():
            if not name in Wrap_A.lifts:
                f = homtype(A)(getattr(A, name))
                if f.arity == 1:
                    Wf = cls.fmap(f)
                elif f.arity == 2:
                    Wf = cls.fmap2(f)
                else:
                    Wf = cls.fmapN(f)
                setattr(Wrap_A, name, Wf)
                Wrap_A.lifts[name] = Wf

    @classmethod
    def fmap(cls, f):
        return lambda x: f(x.data)

    @classmethod
    def fmap2(cls, f):
        print(f.src._tail)
        map_f = lambda x, y: f(x.data, y.data)
        map_f.__name__ = f"map2 {f.__name__}"
        return map_f

    @classmethod
    def fmapN(cls, f):
        src = tuple([cls(si) for si in f.src._tail])
        tgt = cls(f.tgt)
        map_f = Hom(src, tgt)(lambda *xs: f(*(x.data for x in xs)))
        map_f.__name__ = f"mapN {f.__name__}"
        return map_f
