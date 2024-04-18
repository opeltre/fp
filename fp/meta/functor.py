from __future__ import annotations

from .method import Method
from .kind import Kind
from .constructor import Constructor
from .type import Type

import fp.io as io

class Category(Kind):
    
    @Method
    def Hom(T):
        return (T, T), Type



class Functor(Constructor):
    """
    Covariant functors.
    """
    
    src: Category
    tgt: Category
    
    kind = "* -> *"
    arity = 1
    
    @Method
    def fmap(T):
        """
        Map a source arrow `A -> B` to a target arrow `T(A) -> T(B)`.
        """
        return T.src.Hom('A', 'B'), T.tgt.Hom(T('A'), T('B'))

    class _instance_:
        """
        Base class for types of the form `Functor(*As)`. 
        """

        def map(Tx, f, tgt=None):
            """
            Bound `map` method, equivalent to `Functor.fmap(f)(x)`.
            """
            T = Tx._head_
            if isinstance(f, T.src.Hom._top_):
                return T.fmap(f)(Tx)
            src = x._tail_ if T.arity != 1 else Tx._tail_[0]
            f = T.src.Hom(src, tgt)(f)
            return T.fmap(f)(Tx)


class Cofunctor(Constructor):
    """
    Contravariant functors.
    """
    
    src: Category
    tgt: Category

    kind = "* -> *"
    arity = 1

    @Method
    def cofmap(T): 
        return T.src.Hom('X', 'Y'), T.tgt.Hom(T('Y'), T('X'))


class Bifunctor(Functor, Cofunctor):
    """
    Functors with contravariant and covariant arguments.
    """

    kind = "(* , *) -> *"
    arity = 2

    @Method
    def fmap(T):
        return T.src.Hom('A', 'B'), T.tgt.Hom(T('X', 'A'), T('X', 'B'))

    @Method
    def cofmap(T):
        return T.src.Hom('X', 'Y'), T.tgt.Hom(T('Y', 'A'), T('X', 'A'))


class NFunctor(Functor):
    """
    Functors with arbitrary signatures.
    """

    kind = "(*, ...) -> *"
    arity = ...


class ArrowFunctor(Bifunctor):
    """
    Bifunctors with a composition law.
    """

    @Method
    def compose(T):
        return (T('A', 'B'), T('B', 'C')), T('A', 'C')


class HomFunctor(ArrowFunctor):
    """
    Bifunctors with a composition law and an evaluation map.
    """

    @Method
    def eval(T):
        return ('A', T('A', 'B')), 'B'
