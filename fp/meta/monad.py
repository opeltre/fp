from .method import Method
from .type import Type
from .functor import Functor

class Monoidal(Functor):
    """
    Monoidal (a.k.a. Applicative) functors.

    A functor between two monoidal categories respects their monoidal operations.
    In functional programming, one is usually concerned with the category `Type` 
    and its monoidal operation `*` (cartesian product). 
    """

    @Method
    def unit(cls):
        return 'A', cls('A')
    
    @Method
    def lift2(cls):
        return (
            Type.Hom(('A', 'B'), 'C'), 
            Type.Hom((cls('A'), cls('B')), cls('C')),
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
    @Method
    def unit(cls):
        return 'A', cls('A')

    @Method
    def join(cls):
        return cls(cls('A')), cls('A')

    @Method
    def bind(cls):
        return (cls('A'), Type.Hom('A', cls('B'))), cls('B')

    class _defaults_(Functor._defaults_):

        @classmethod
        def bind(cls, ma, mf):
            mmb = cls.fmap(mf)(ma)
            return cls.join(mmb)

        @classmethod
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
                        tgt = C,
                    ),
                    tgt = Hom(cls(B), cls(C))
                )

    class _instance_(Functor._instance_):
        
        @property
        def _monad_(ma):
            return ma._head_

        def bind(ma, mf):
            monad = ma._monad_
            return ma._monad_.bind(ma, mf)

        def __rshift__(ma, mf):
            return ma.bind(mf)
