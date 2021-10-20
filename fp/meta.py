class Kind(type):
    """ Type kinds. """

    def __new__(cls, name, bases, dct):
        """ Create a kind. """
        T = super().__new__(cls, name, bases, dct)
        T.__repr__ = lambda t: f"{type(t)} {t.__name__}"
        return T

    def __repr__(self): 
        """ Show type name. """
        return f"{self} : {self.kind}"

    def __str__(self):
        return self.__name__.replace("Kind", "")


class TypeKind(type, metaclass=Kind):
    """ Type class. """
    
    kind = "*" 

    def __new__(cls, name, bases, dct):
        """ Create a new type. """
        T = super().__new__(cls, name, bases, dct)
        return T
    
    def __repr__(self):
        """ Show type name. """
        return f"{self.__name__}"

class Type(metaclass=TypeKind):
    pass


class FunctorKind(type, metaclass=Kind):
    """ Functor type class. """
    
    kind    = "* -> *" 
    arity   = 1

    def __new__(cls, name, bases, dct):
        """ Create a functorial type constructor T: a -> T a. """
        T = super().__new__(cls, name, bases, dct)
        T.types = {}
        T.__new__ = cls.new_method(T.__new__)
        return T

    @staticmethod
    def new_method(new):
        """ Type constructor T: A -> T A with lookup for A. """
        def _new_ (cls, *As):
            """ Look for T A in or return a new type T A. """
            #--- Check arity 
            if cls.arity - len(As) != 0:
                raise TypeError("Wrong kind")
            #--- Return type if exists 
            if As in cls.types:
                return cls.types[As]
            #--- Create new type otherwise 
            TA = new(cls, *As)
            TA.functor  = cls 
            TA.__name__ = cls.name(*As)
            cls.types[As] = TA
            cls.__init__(TA, *As)
            return TA
        return _new_


class Functor(metaclass=FunctorKind):

    def __init__(TA, A):
        pass

    @classmethod
    def fmap(cls, f):
        raise NotImplementedError()
    
    @classmethod
    def name(cls, A):
        return f"{cls.__name__} {A.__name__}"


class BifunctorKind(FunctorKind):
    
    kind  = "(*, *) -> *"
    arity = 2 
    
class Bifunctor(metaclass=BifunctorKind):

    def __init__(TAB, A, B):
        pass

    def __new__(cls, A, B):
        class TAB (Type):
            pass
        TAB.__name__ = f"{A} -> {B}"
        return TAB

    @classmethod
    def name(cls, A, B):
        return f"{cls.__name__} ({A.__name__}, {B.__name__})"
