from __future__ import annotations

from .kind import Kind
from .type import Type, TypeClass, Variable, Constructor
from .method import Method

import fp.io


class ConstructorClass(Kind):

    kind = "(*, ...) -> *"
    arity = -1

    @Method
    def new(cls):
        """Return a new type"""
        return Hom(Type, Type)

    def __new__(cls, name, bases, dct):
        """Initialize a constructor class"""
        constructor = super().__new__(cls, name, bases, dct)

        # --- register methods
        for k, v in cls._methods.items():
            if k in dct:
                method = dct[k]
                setattr(constructor, k, method)
            else:
                print(f"Missing method {k}: {constructor.__name__} <= {cls.__name__}")

        # --- decorate constructor.new
        T_new = constructor.__new__

        def new(T, *As, **Ks):
            # get __name__
            name = T.name(*As)
            # inherit from T.new(*As)
            bases = (T.new(*As, **Ks),)
            TA = TypeClass.__new__(T, name, bases, {})
            # symbolic (T)::(*As) ---
            TA._head = T
            TA._tail = tuple(As)
            # init
            T.__init__(TA, *As)
            return TA

        constructor.__new__ = new

        return constructor

    def name(T, *As):
        """
        Return `__name__` string of output type.

        Override as a classmethod from `ConstructorClass` instances as needed.
        """
        names = [A.__name__ if "__name__" in dir(A) else str(A) for A in As]
        tail = ", ".join(names)
        return f"{T.__name__} ({tail})" if len(names) > 1 else f"{T.__name__} {tail}"


class FunctorClass(ConstructorClass):

    kind = "* -> *"
    arity = 1
    src, tgt = Type, Type

    @Method
    def new(cls):
        return Hom(Type, Type)

    @Method
    def fmap(cls):
        T = cls if callable(cls) else Constructor("T")
        return Hom(Hom("A", "B"), Hom(T("A"), T("B")))

    def __matmul__(F, G):
        """Composition of functors."""

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


class Functor(TypeClass, metaclass=FunctorClass):
    """Functor type class."""

    def __new__(cls, *As):
        name = cls.name(*As)
        bases = (cls.new(*As),)
        TA = super().__new__(cls, name, bases, {})
        cls.__init__(TA, *As)
        return TA

    def __init__(TA, *As):

        def map(x, f, tgt=None):
            T = TA.__class__
            if not isinstance(f, T.src.Hom):
                src = TA._tail if T.arity != 1 else TA._tail[0]
                f = T.src.Hom(src, tgt)(f)
                return T.fmap(f)(x)
            return T.fmap(f)(x)

        TA.map = map

    @classmethod
    def fmap(cls, f):
        raise NotImplementedError(f"{cls}.fmap")

    @classmethod
    def new(cls, *As):
        return Type


class BiFunctor(Functor):

    kind = "(*, *) -> *"
    arity = 2


class NFunctor(Functor):

    kind = "(*, ..., *) -> *"
    arity = -1
