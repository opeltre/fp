from contextlib import contextmanager

from typing import Callable, Iterable

from fp.meta import Monad, HomFunctor, Var
from fp.cartesian import Type, Hom, Prod
import fp.io as io

Point = Type.Unit()

class StateMonad(Type, metaclass=Monad):
    """
    State monad.

    The monad `State S` maps any type `A` to the stateful computation 
    type `State S A`. 


    """
    
    _state_ : Type = Var("S")

    src = Type
    tgt = Type

    @classmethod
    def new(cls, A):
        return State(cls._state_, A)
    
    def _post_new_(StA, A):
        StA._head_ = StA.__class__
        StA._tail_ = (StA._state_, StA._value_)
        
    @classmethod
    def _subclass_(cls, *xs, **ys):
        print(cls, "_subclass_", xs[:2])
        return Monad.__new__(cls, *xs, **ys)
    
    @classmethod
    def fmap(cls, f):
        """
        Map pure callables `A -> B` by post-transform of the return value.
            
            >>> State.fmap(f)(st_a)(s0) == st_a.exec(s0), f(st_a.eval(s0))
            True
        """ 
        @Hom(cls(f.src), cls(f.tgt))
        def push_f(st_a):
            return st_a.then(lambda s, a: (s, f(a)), tgt=f.tgt)
        
        push_f.__name__ = "map " + f.__name__
        return push_f

    @classmethod
    def unit(cls, a=Type.Unit()):
        """
        Return a value `a : A`.
        """
        S, A = cls._state_, type(a)
        unit_a = cls(A)(lambda s: (s, a))
        unit_a.__name__ = str(a)
        return unit_a
    
    @classmethod
    def join(cls, ffa):
        """
        Evaluate the returned stateful subprocess.
        """
        S, A = cls._state_, ffa._value_._value_
        def state_join(s0):
            """
            Flattened stateful computation.
            """
            s1, fa = ffa.run(s0)
            return  fa.run(s1)
        return cls(A)(state_join)

    @classmethod
    def gets(cls, f):
        """
        Get and return an image of the state by `f : S -> A`.
        """
        S, A = f.src, f.tgt
        io.asserts.subclass(S, f.src)
        gets_f = cls.unit(Point).gets(f)
        gets_f.__name__ = "gets " + f.__name__
        return gets_f
    
    @classmethod
    def puts(cls, f):
        """
        Update the state by an image of `f : A -> S`.
        """
        S, A = f.tgt, f.src
        io.asserts.subclass(A, f.src)

        @Hom(A, cls(A))
        def puts_f(a):
            return cls.unit(Point).puts(f)

        puts_f.__name__ = "puts " + f.__name__
        return puts_f
    
    @classmethod
    def put(cls, s):
        """
        Update the state and return `()`.
        """
        put_s = cls.unit().put(s)
        put_s.__name__ = "put " + str(s)
        return put_s
    
    @classmethod
    def chain(cls, *sts):
        ...

class State(Hom, metaclass=HomFunctor):
    """
    State bifunctor and monad. 

    The type `State(S, A)` describes stateful computations yielding a return 
    value of type `A` while acting on the state type `S`. The isomorphism::

        S -> (S, A) ~= State(S, A)
    
    may be used as a decorator do define stateful computations.::

        >>> @State(Str, Str)
        ... def popchar(s):
        ...     return s[1:], s[0]
        ...
        >>> popchar.run("cat")
        (Str, Str) : ('at', 'c')

    Calling `State` with only one argument `S` will return a `StateMonad` subclass
    with a class attribute `_state_`. Calling this monad on a type `A` will also 
    return the type `State(S, A)`, i.e.::
        
        >>> isinstance(State(Str), Monad)
        True
        >>> State(Str, Int) is State(Str)(Int)
        True
        # monadic types `State S A` are of type `State`
        >>> type(State(Str)(Int) is State)
        True

    Note that this is an important difference with the `Stateful` implementation, 
    which puts the emphasis on state-type specific implementations. Using the 
    `State` bifunctor may be considered safer at a little convenience cost
    (the global class state of `Stateful(S, s0)` types). 
    """

    class Object(Monad._instance_, Hom.Object): 
        """
        Stateful computation.
        """
        
        def __init__(self, pipe, initial=None):
            self.__name__ = pipe.__name__ if hasattr(pipe, '__name__') else "st"
            super().__init__(pipe)
            self._initial_ = initial

        @property
        def _monad_(self):
            return self._head_(self._state_)
        
        def map(self, f):
            map_f = self._monad_.fmap(f)(self)
            map_f.__name__ = self.__name__ + " > " + f.__name__
            return map_f
        
        def bind(self, mf):
            maf = super().bind(mf)
            maf.__name__ = self.__name__ + " >> " + mf.__name__
            return maf
        
        def run(self, s=None):
            if s is None:
                s = self._initial_
            return Hom.Object.__call__(self, s)

        def exec(self, s=None):
            return self.run(s)[0]

        def __call__(self, s=None):
            return self.run(s)[1]
        
        @contextmanager
        def use(self, state):
            try:
                s0 = self._initial_
                self._initial_ = state
                s1, a = self.run(state)
                yield self._monad_.put(s1).unit(a)
            finally:
                self._initial_ = s0
        
        # --- Compositions by method chaining ---

        def then(self, f, tgt=None):
            if tgt is None: 
                tgt = f.tgt[1]
            pipe = (*self._pipe, lambda pair: f(*pair))
            out = self._monad_(tgt)(pipe, self._initial_)
            out.__name__ = self.__name__ + " ; " + f.__name__
            return out

        def gets(self, f, tgt=None):
            tgt = tgt or f.tgt
            if callable(f):
                get_f = lambda s, a: (s, f(s))
            elif isinstance(f, str):
                get_f = lambda s, a: (s, getattr(s, f))
            get_f.__name__ = "get " + f.__name__
            return self.then(get_f, tgt=tgt)

        def put(self,  s):
            out = self.then(lambda *_: (s, ()), tgt=Type.Unit)
            out.__name__ = self.__name__ + " >> put " + str(s)
            return out
        
        def unit(self, a):
            unit_a = lambda s, _: (s, a)
            unit_a.__name__ = "return " + str(a)
            out = self.then(unit_a, type(a))
            return out

        def puts(self, f):
            puts_f = lambda s, a: (f(s), a)
            puts_f.__name__ = "put " + f.__name__
            return self.then(puts_f, tgt=self._value_)
        
    @classmethod
    def new(cls, S, A=...):
        if A is ...:
            class State_S(StateMonad):
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
        return cls("S").fmap(f)

    @classmethod
    def _get_name_(cls, S, A=...):
        if A is ...:
            return f'{cls.__name__} {S}'
        return ' '.join((cls.__name__, str(S), str(A)))
    
    @classmethod
    def gets(cls, f):
        S, A = f.src, f.tgt
        gets_f = cls(S, A)(lambda s: (s, f(s)))
        gets_f.__name__ = "gets " + f.__name__
        return gets_f

    @classmethod
    def puts(cls, f):
        S, A = f.tgt, f.src

        @Hom(A, cls(S, A))
        def puts_f(a):
            return cls(S, A)(lambda s: (f(a), a))

        puts_f.__name__ = "puts " + f.__name__
        return puts_f
    
    @classmethod
    def put(cls, s):
        S = type(s)
        put_s = cls(S, Type.Unit)(lambda s0: (s, ())) 
        return put_s
       
    @classmethod
    def eval(cls, s, f):
        s1, a = super().eval(s, f)
        return a

    @classmethod
    def _subclass_(cls, *xs, **ys):
        print(cls, "_subclass_", xs[:2])
        return Monad.__new__(cls, *xs, **ys)



class StatefulMonad(StateMonad):
    """
    Stateful Monads on a pointed state type.

    Fully stateful monads are defined by both a state 
    type `S` and an initial state `_initial_ : S`.

        >>> MyString = Stateful(Str, "Hello World!")

    """
    _state_ : Type = Var("S")
    _initial_ : Var("S")

    class Object(State.Object, Hom.Object):
        
        arity = 1
        
        @property
        def _monad_(self):
            return self._head_
        
        def __init__(self, pipe, initial=None):
            super().__init__(pipe, initial)
        
        def run(self, s=None):
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
            _state_ = cls._state_,
            _value_ = A,
            src = cls._state_,
            tgt = Prod(cls._state_, A),
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
            dct = dict(
                _state_ = S,
                _initial_ = initial
            )
        else: 
            name, bases = S, initial
        SA = super().__new__(cls, name, bases, dct)
        super().__init__(SA, name, bases, dct)
        SA._head_ = cls
        SA._tail_ = (S,)
        return SA

    def __init__(SA, A, initial=None, dct=None):
        ...
