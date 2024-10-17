from contextlib import contextmanager

from fp.meta import Monad, Var
from fp.cartesian import Type, Hom, Prod
import fp.io as io

from .state import StateMonad, State


class StatefulMonad(StateMonad):
    """
    Stateful Monads on a pointed state type.

    Fully stateful monads are defined by both a state
    type `S` and an initial state `_initial_ : S`.

        >>> MyString = Stateful(Str, "Hello World!")

    """

    _state_: Type = Var("S")
    _initial_: Var("S")

    class Object(State.Object, Hom.Object):

        arity = 1

        @property
        def _monad_(self):
            return self._head_

        def __init__(self, pipe, initial=None):
            super().__init__(pipe, initial)

        def run(self, s=None):

            # TODO: return Hom(src | None, tgt) supporting optional s0
            if s is None:
                s = self.__class__._initial_
            return super().run(s)

        @property
        def state(self):
            return self.run()[0]

        @property
        def value(self):
            return self.run()[1]

    @classmethod
    @contextmanager
    def use(cls, s0: Var("S")):
        """
        Context manager for the `_initial_` class attribute.

        Within a managed block, evaluation of any stateful
        instance will be computed from `s0`.

        Yields
        ------
        put_s0 : cls(Type.Unit)
            a stateful instance with initial state `s0` and
            returning `()`.
        """
        s1 = cls._initial_
        try:
            cls._initial_ = s0
            yield cls.put(s0)
        finally:
            cls._initial_ = s1

    @classmethod
    def new(cls, A):
        name = cls._get_name_(A)
        bases = (cls.Object,)
        dct = dict(
            _state_=cls._state_,
            _value_=A,
            src=cls._state_,
            tgt=Prod(cls._state_, A),
        )
        SA = Type.__new__(cls, name, bases, dct)
        Type.__init__(SA, name, bases, dct)
        SA._monad_ = cls
        return SA


class Stateful(Monad):

    _defaults_ = StatefulMonad

    def __new__(cls, S, initial=None, dct=None):
        if isinstance(S, (Type, type)):
            name = "Stateful(" + S.__name__ + ")"
            bases = ()
            dct = dict(_state_=S, _initial_=initial)
        else:
            name, bases = S, initial
        SA = super().__new__(cls, name, bases, dct)
        super().__init__(SA, name, bases, dct)
        SA._head_ = cls
        SA._tail_ = (S,)
        return SA

    def __init__(SA, A, initial=None, dct=None): ...

    @property
    def get(self):
        return self.gets(Hom.id(self._state_))
