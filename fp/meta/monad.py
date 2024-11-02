from .type_class_method import TypeClassMethod
from .method import ClassMethod
from .type import Type
from .functor import Functor


class Monoidal(Functor):
    """
    Monoidal (a.k.a. Applicative) functors.

    A functor between two monoidal categories respects their monoidal operations.
    In functional programming, one is usually concerned with the category `Type`
    and its monoidal operation `*` (cartesian product).
    """

    @TypeClassMethod
    def unit(cls):
        return "A", cls("A")

    @TypeClassMethod
    def lift2(cls):
        return (
            Type.Hom(("A", "B"), "C"),
            Type.Hom((cls("A"), cls("B")), cls("C")),
        )


class Monad(Monoidal):
    """
    Monads.

    A monad is a monoid in the category of functors `Type -> Type`.

    The `join` operation is referred to as monadic composition,
    examples include:
        - flattening of lists, trees, ...
        - concatenation of logs, error messages, ...
        - subprocess execution, asynchronous await, ...
    """

    @TypeClassMethod
    def unit(cls):
        return "A", cls("A")

    @TypeClassMethod
    def join(cls):
        return cls(cls("A")), cls("A")

    @TypeClassMethod
    def bind(cls):
        return (cls("A"), Type.Hom("A", cls("B"))), cls("B")

    class _defaults_(Functor._defaults_):

        @ClassMethod
        def join(cls, mma):
            MA = mma._tail_[0]
            return mma.bind(Type.Hom.id(MA))

        @ClassMethod
        def fmap(cls, f):
            """
            Default implementation of `fmap(f)` as `bind ... (unit @ f)`.
            """

            @Type.Hom(f.src, cls(f.tgt))
            def unit_f(a):
                return cls.unit(f(a))

            @Type.Hom(cls(f.src), cls(f.tgt))
            def fmap_f(ma):
                return cls.bind(ma, unit_f)

            fmap_f.__name__ = "map " + f.__name__
            return fmap_f

        @ClassMethod
        def bind(cls, ma, mf):
            """
            Default implementation of `bind` in terms of `join`.
            """
            mmb = cls.fmap(mf)(ma)
            return cls.join(mmb)

        @ClassMethod
        def lift2(cls, f):
            """
            Default implementation of `lift2` by nested binds.
            """
            A, B = f.src
            C = f.tgt
            Hom = cls.src.Hom

            @Hom((cls(A), cls(B)), cls(C))
            def lifted(ma, mb):
                return ma.bind(
                    lambda a: mb.bind(
                        lambda b: cls.unit(f(a, b)),
                        tgt=C,
                    ),
                    tgt=Hom(cls(B), cls(C)),
                )

    class TopType(Functor.TopType):

        @property
        def _monad_(ma):
            return ma._head_

        def bind(ma, mf):
            monad = ma._monad_
            return ma._monad_.bind(ma, mf)

        def __rshift__(ma, mf):
            return ma.bind(mf)
