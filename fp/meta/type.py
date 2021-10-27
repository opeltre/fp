from .kind import Kind

class TypeMeta(type, metaclass=Kind):
    """ Type class. """
    
    kind = "*" 

    def __new__(cls, name, bases, dct):
        """ Create a new type. """
        T = super().__new__(cls, name, bases, dct)
        T.__repr__ = cls.repr_method(T.__repr__)
        return T
    
    @staticmethod
    def repr_method(rep):
        return lambda x: f"{type(x)} : {rep(x)}"

    def __repr__(self):
        """ Show type name. """
        return f"{self.__name__}"


class Type(metaclass=TypeMeta):
    pass
