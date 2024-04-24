from fp.meta import Monad, HomFunctor
from fp.cartesian import Type, Hom, Prod

from typing import Callable, Iterable

class Stateful(Type, metaclass=Monad):

    _state_ : Type

    @classmethod
    def new(cls, A):
        return State(cls._state_, A)
    
    @classmethod
    def _subclass_(cls, *xs, **ys):
        print(cls, "_subclass_", xs[:2])
        #return Monad.__new__(cls, *xs, **ys)
    
    @classmethod
    def fmap(cls, f):
        return State.fmap(f)

    @classmethod
    def unit(cls, a): 
        S, A = cls._state_, type(a)
        return cls(A)(lambda s: (s, a))

    @classmethod
    def join(cls, ffa):
        S, A = cls._state_, ffa._value_._value_
        def state_join(s0):
            """
            Flattened stateful computation.
            """
            s1, fa = ffa(s0)
            return fa(s1)
        return cls(A)(state_join)


class State(Hom, metaclass=HomFunctor):

    class _top_(Hom._top_): 
       ... 
    
    @classmethod
    def new(cls, S, A=...):
        if A is ...:
            class State_S(Stateful):
                _state_ = S

            return State_S
        
        src, tgt = S, Prod(S, A)
        State_SA = super().new(src, tgt)
        State_SA._state_ = S
        State_SA._value_ = A
        return State_SA
    
    @classmethod
    def _post_new_(cls, S, A=..., *xs):
        ...

    @classmethod
    def fmap(cls, f):
        return super().fmap(lambda s, a: (s, f(a)))

    @classmethod
    def _get_name_(cls, S, A=...):
        if A is ...:
            return f'{cls.__name__} {S}'
        return ' '.join((cls.__name__, str(S), str(A)))
    
    @classmethod
    def eval(cls, s, f):
        return f(s)
