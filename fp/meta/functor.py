import abc 

from .kind import Kind

class FunctorMeta(abc.ABCMeta, metaclass=Kind):
    """ Functor type class. """
    
    kind    = "* -> *" 
    arity   = 1

    lifts = {}
    
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
            #--- Return type if it exists 
            if As in cls.types:
                return cls.types[As]
            #--- Create and index new type otherwise 
            TA = new(cls, *As)
            cls.types[As] = TA
            TA.functor  = cls
            TA.types    = As 
            if 'name' in dir(cls):
                TA.__name__ = cls.name(*As)
            else:
                TA.__name__ = cls.__name__ + ' ' + ' '.join([str(A) for A in As])
            cls.__init__(TA, *As)
            #--- 
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

    def __init__(self, *xs):
        pass
        
    @classmethod
    @abc.abstractmethod
    def fmap(cls, f):
        ...
     
    @classmethod
    def name(cls, A):
        return (f"{cls.__name__} {A.__name__}" 
                if '__name__' in dir(A) else
                f"{cls.__name__} {A}")
        

class Bifunctor(metaclass=BifunctorMeta):

    @classmethod
    def name(cls, A, B):
        return f"{cls.__name__} ({A.__name__}, {B.__name__})"