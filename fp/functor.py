class Functor(type):
    """ Functor type class. """

    types = {}

    def __repr__(cls):
        """ Show type without <type '...'> brackets. """
        return f"{cls.__name__} {cls.arg.__name__}"

    @staticmethod
    def new_method(new):
        """ Decorate type-values creation by looking up instances. """
        def _new_(cls, A):
            cls.arg = A
            #--- Return type if exists ---
            if A.__name__ in cls.types:
                return cls.types[A.__name__]
            #--- Return new type otherwise ---
            FA   = new(cls, A)
            FA_t = super().__new__(cls, f"List {A.__name__}", (FA,), {})
            cls.types[A.__name__] = FA_t
            return FA_t
        return _new_