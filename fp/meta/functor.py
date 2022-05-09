import abc 

from .kind import Kind

class FunctorMeta(abc.ABCMeta, metaclass=Kind):
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
        """ Type constructor T: A -> T A with lookup for known input A. """
        def _new_ (cls, *As):
            """ Look for T A in T.types or return a new type T A. """
            #--- Check abstract methods 
            if len(cls.__abstractmethods__):
                raise TypeError(
                    f"Abstract methods missing in type {cls}")
            #--- Check arity 
            if cls.arity != 'n' and cls.arity - len(As) != 0:
                raise TypeError(
                    f"Wrong kind : could not apply {cls.arity}-ary " +\
                    f"functor {cls} to input {As}")
            #--- Return type if exists 
            if As in cls.types:
                return cls.types[As]
            #--- Create new type otherwise 
            TA = new(cls, *As)
            TA.functor  = cls 
            TA.__name__ = cls.name(*As)
            cls.types[As] = TA
            #cls.__init__(TA, *As)
            return TA
        return _new_


class BifunctorMeta(FunctorMeta):
    
    kind  = "(*, *) -> *"
    arity = 2 

    
class NFunctorMeta(FunctorMeta):
    
    kind  = "(*, ...) -> *"
    arity = 'n'


#--- Instances ---

class Functor(metaclass=FunctorMeta):
    """ Functor type class. """

    @classmethod
    @abc.abstractmethod
    def fmap(cls, f):
        ...

    @classmethod
    def name(cls, A):
        return f"{cls.__name__} {A.__name__}"
        

class Bifunctor(metaclass=BifunctorMeta):

    @classmethod
    def name(cls, A, B):
        return f"{cls.__name__} ({A.__name__}, {B.__name__})"