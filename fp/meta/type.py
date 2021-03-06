from .kind import Kind
from colorama import init, Style

init()

class TypeMeta(type, metaclass=Kind):
    """ Base type class. """
    
    kind = "*" 

    def __new__(cls, name, bases, dct):
        """ Create a new type. """
        T = super().__new__(cls, name, bases, dct)
        T.__str__  = cls.str_method(T.__repr__)
        T.__repr__ = cls.repr_method(T.__repr__)
        if not "cast" in dir(T):
            T.cast = cls.cast_method(T)
        return T
    
    @staticmethod
    def repr_method(rep):
        def _rep_(x):
            tx = f"{type(x)} : "
            indent = len(tx)
            rx = rep(x)
            tx = Style.DIM + tx + Style.NORMAL
            if rx[:len(tx)] == tx:
                return rx
            else:
                return tx + rx.replace("\n", "\n" + " " * indent)
        return _rep_

    @staticmethod
    def str_method(rep):
        return lambda x: rep(x)
    
    @staticmethod
    def cast_method(T):

        def _cast_(x):
            if isinstance(x, T): 
                return x
            try: 
                Tx = T(x) 
                return _cast_(Tx)
            except:
                raise TypeError(f"Could not cast {type(x)} to type {T}.")

        return _cast_

    def __repr__(self):
        """ Show type name. """
        return f"{self.__name__}"


#--- Instances ---

class Type(metaclass=TypeMeta):
    pass
