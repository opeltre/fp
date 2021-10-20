class List(type, metaclass=Functor):
    """ The List Functor. """

    @classmethod
    def fmap(cls, f):
        """ List map: (A -> B) -> List A -> List B """
        src, tgt = cls(f.src), cls(f.tgt)
        def mapf(xs):
            if not isinstance(xs, src):
                raise TypeError(f"Input not of type {src}")
            return tgt([f(x) for x in xs])
        return Arrow([src, tgt], mapf)


    @Functor.new_method
    def __new__(cls, A):
        """ Return the type List A. """

        class ListA(list):
            def __init__(self, it):
                if 0 == sum((not isinstance(x, A) for x in self)):
                    super().__init__((x for x in it))
                super().__init__((A(x) for x in it))

        return ListA
