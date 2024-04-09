from .kind      import Kind


from .functor   import  Functor, FunctorClass,\
                        Bifunctor, BifunctorClass, \
                        NFunctorClass

from .arrow     import ArrowClass, Arrow, Prod
from .hom       import Hom

from .type      import Type, TypeClass, Variable, Constructor
from .alg       import RingClass, AlgClass, Bool

__all__ = [
    'Kind',
    'Functor',
    'FunctorClass',
    'Bifunctor', 
    'BifunctorClass',
    'NFunctorClass',
    'ArrowClass',
    'Arrow',
    'Hom',
    'Prod',
    'Type',
    'TypeClass', 
    'Variable',
    'Constructor',
    'RingClass', 
    'AlgClass',
    'Bool',
]
