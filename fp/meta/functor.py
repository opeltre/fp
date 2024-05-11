from __future__ import annotations

from .method import Method
from .kind import Kind
from .constructor import Constructor, Var
from .type import Type

import fp.io as io

class Category(Kind):
    
    @Method
    def Hom(T):
        return (T, T), Type


Args = tuple[int] | type(...)

class Functor(Constructor):
    """
    Covariant functors.
    """
    
    src: Category
    tgt: Category

    arity : int = 1
    _kind_ : tuple[Args, Args] = ..., ()

    class _instance_:
        """
        Base class for types of the form `Functor(*As)`. 
        """

        def map(Tx, f, tgt=None):
            """
            Bound `map` method, equivalent to `Functor.fmap(f)(x)`.
            """
            T = Tx._head_
            if isinstance(f, T.src.Hom.Object):
                return T.fmap(f)(Tx)
            src = x._tail_ if T.arity != 1 else Tx._tail_[0]
            f = T.src.Hom(src, tgt)(f)
            return T.fmap(f)(Tx)
    
    @property
    def kind(T: type) -> str:
        """String representation of functor signature."""
        return Kind._functor_kind_(T.arity, *T._kind_)
        
    @Method
    def fmap(T):
        """
        Map a source arrow `A -> B` to a target arrow `T(A) -> T(B)`.
        """
        src = T.src if hasattr(T, "src") else Type
        tgt = T.tgt if hasattr(T, "tgt") else Type
        if T.arity == 1:
            return src.Hom('A', 'B'), tgt.Hom(T('A'), T('B'))
        elif T.arity is ...:
            source = src.Hom("A", "B"), Var("...")
            target = tgt.Hom(T("A", Var("...").src), T("B", Var("...").tgt))
            return source, target


class Cofunctor(Constructor):
    """
    Contravariant functors.
    """
    
    src: Category
    tgt: Category
    
    arity = 1
    _kind_ = (), ...
    
    @property
    def kind(T):
        return Kind._functor_kind_(T.arity, *T._kind_)

    @Method
    def cofmap(T): 
        src = T.src if hasattr(T, "src") else Type
        tgt = T.tgt if hasattr(T, "tgt") else Type
        if T.arity == 1:
            return src.Hom('A', 'B'), tgt.Hom(T('B'), T('A'))
        elif T.arity is ...:
            source = src.Hom("A", "B"), Var("...")
            target = tgt.Hom(T("B", Var("...").tgt), T("A", Var("...").src))
            return source, target

        return T.src.Hom('X', 'Y'), T.tgt.Hom(T('Y'), T('X'))

class Bifunctor(Functor):
    """
    Functors with both contravariant and covariant arguments.
    """

    arity = 2
    _kind_ = (1,), (0,)

    @Method
    def fmap(T):
        return T.src.Hom('A', 'B'), T.tgt.Hom(T('X', 'A'), T('X', 'B'))

    @Method
    def cofmap(T):
        return T.src.Hom('X', 'Y'), T.tgt.Hom(T('Y', 'A'), T('X', 'A'))


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


class NFunctor(Functor):
    """
    Functors with arbitrary signatures.
    """

    kind = "(*, ...) -> *"
    arity = ...
    _kind_ = ..., ()
