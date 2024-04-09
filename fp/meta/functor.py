import abc 

from .kind import Kind
from .type import Type, TypeClass, Variable


class FunctorClass(abc.ABCMeta, metaclass=Kind):
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
    
    @classmethod
    def instance(cls, ty: type):
        return cls.__new__(cls, ty.__name__, ty.__bases__, dict(ty.__dict__))

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
            As = tuple(cls.parse_type(A) for A in As)
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
            #--- Return type variable if one type is a parameter
            var = any(isinstance(A, Variable) for A in As)
            return TA if not var else Variable(TA.__name__, (TA,))
        return _new_

    @classmethod
    def parse_type(cls, A):
        if isinstance(A, list): 
            return tuple(A)
        if isinstance(A, str):
            return Variable(A)
        else:
            return A

    def eq_method(TA, TB):
        """ Compare functorial types """
        if not ("functor" in dir(TB) and "types" in dir(TB)):
            return False
        return TA.functor == TB.functor and TA.types == TB.types


class BifunctorClass(FunctorClass):
    
    kind  = "(*, *) -> *"
    arity = 2 

    
class NFunctorClass(FunctorClass):
    
    kind  = "(*, ...) -> *"
    arity = 'n'


#--- Instances ---

class Functor(metaclass=FunctorClass):
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
        

class Bifunctor(metaclass=BifunctorClass):

    @classmethod
    def name(cls, A, B):
        return f"{cls.__name__} ({A.__name__}, {B.__name__})"
