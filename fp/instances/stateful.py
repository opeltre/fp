from __future__ import annotations
from typing import Literal

from contextlib import contextmanager

from fp.meta import Monad, Var
from fp.cartesian import Type, Hom, Prod
import fp.io as io

from .state import StateMonad, State


class StatefulObject(State.Object, Hom.Object):
    """Stateful computation.

    In contrast with `State.Object` instances, this class is meant to emulate
    computations that depend on a global shared state. See :class:`Stateful`.

    The `Stateful` constructor's `.use` context manager provides a single
    entry point for changing the global state, from which every `Stateful.Object`
    reads from.

    In addition to the `State.Object` interface, stateful objects expose the
    following properties and methods:

    * `self.state` evaluates the final state,
    * `self.value` evaluates the read-out value,
    * `self.mock()` returns a read-only getter to the read-out value,
      providing e.g. a lazy reference to the global state when used
      on `self._monad_.get`.
    """

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

    def mock(self, method: Literal["state"] | Literal["value"] = "value"):
        return StatefulMock(self, method)

    @property
    def state(self):
        return self.run()[0]

    @property
    def value(self):
        return self.run()[1]


class StatefulMonad(StateMonad):
    """
    Stateful Monads on a pointed state type.

    Fully stateful monads are defined by both a state
    type `S` and an initial state `_initial_ : S`.

        >>> MyString = Stateful(Str, "Hello World!")

    """

    _state_: Type = Var("S")
    _initial_: Var("S")

    Object = StatefulObject

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


class StatefulMock:
    """Read-only mock of a final stateful value."""

    def __init__(self, stateful: Stateful, mode: str = "value"):
        self._stateful_ = stateful
        self._idx_ = 0 if mode == "state" else 1

    def __getattr__(self, attr):
        try:
            return super().__getattr__(self, attr)
        except AttributeError:
            return getattr(self._stateful_.run()[self._idx_], attr)

    def __repr__(self):
        return str(self._stateful_)


class Stateful(Monad):
    """Stateful bifunctor and monad.

    The `Stateful(S, A) ~ S -> (S, A)` type provides a similar interface to its
    homologous :class:`State` type, but differs by handling a global default
    state accessed by the `Stateful.use` context manager.
    """

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
