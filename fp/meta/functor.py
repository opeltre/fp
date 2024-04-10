from __future__ import annotations

from .kind import Kind
from .type import Type, TypeClass, Variable, Constructor
from .method import Method
from .constructor import ConstructorClass

import fp.io


class FunctorType:
    """
    Base class for types of the form `Functor(*As)`. 
    """
    def map(x, f, tgt=None):
        """
        Bound `map` method, equivalent to `Functor.fmap(f)(x)`.
        """
        T = x._head
        if not True:
            src = x._tail if T.arity != 1 else x._tail[0]
            f = T.src.Hom(src, tgt)(f)
            return T.fmap(f)(x)
        return T.fmap(f)(x)


class FunctorClass(ConstructorClass):

    kind = "* -> *"
    arity = 1
    src, tgt = Type, Type

    @Method
    def fmap(F):
        """
        Functorial transformation of morphisms.
        """
        return F.src.Hom("A", "B"), F.tgt.Hom(F("A"), F("B"))
    
    def __matmul__(F, G):
        """
        Composition of functors.
        """

        class FG(Functor):

            kind = G.kind
            arity = G.arity
            src, tgt = G.src, F.tgt

            def __new__(cls, *As, **Ks):
                return F(G(*As, **Ks))

            @classmethod
            def fmap(cls, f):
                return F.fmap(G.fmap(f))

        FG.__name__ = f"{F.__name__} @ {G.__name__}"
        return FG
    
    @classmethod
    def _base(cls):
        return FunctorType


class BifunctorClass(FunctorClass):

    kind = "(*, *) -> *"
    arity = 2


class NFunctorClass(FunctorClass):

    kind = "(*, ...) -> *"
    arity = ...


class Functor(metaclass=FunctorClass):
    """Functor type class."""

    def fmap(cls, f):
        raise NotImplementedError(f"{cls}.fmap")

    def new(cls, *As):
        return Type
