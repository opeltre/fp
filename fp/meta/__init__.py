from .kind import Kind
from .method import Method
from .type import Type, TypeClass, Variable, Constructor
from .constructor import ConstructorClass

from .functor import Functor, FunctorClass, BifunctorClass, NFunctorClass
from .arrow import ArrowClass, Arrow, HomClass, Hom
from .prod import Prod


from .alg import RingClass, AlgClass, Bool

__all__ = [
    "Kind",
    "Method",
    "ConstructorClass",
    "Functor",
    "FunctorClass",
    "BifunctorClass",
    "NFunctorClass",
    "ArrowClass",
    "Arrow",
    "HomClass",
    "Hom",
    "Prod",
    "Type",
    "TypeClass",
    "Variable",
    "Constructor",
    "RingClass",
    "AlgClass",
    "Bool",
]

# Category of types: move this
Type.Hom = Hom
