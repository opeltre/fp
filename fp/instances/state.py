from contextlib import contextmanager

from typing import Callable, Iterable

from fp.meta import Monad, HomFunctor, Var
from fp.cartesian import Type, Hom, Prod
import fp.io as io

Point = Type.Unit()

class StateMonad(Type, metaclass=Monad):
    
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

        def id_f(pair):
            s, a = pair
            return s, f(a) 
        id_f.__name__ = f"map {f.__name__}"

        @Hom(cls(f.src), cls(f.tgt))
        def push_f(st_a):
            St_b = State(st_a._state_, f.tgt)
            return St_b((*st_a._pipe, id_f))
        
        push_f.__name__ = "map " + f.__name__
        return push_f

        return State.fmap(f)

    @classmethod
    def unit(cls, a=Type.Unit()):
        S, A = cls._state_, type(a)
        unit_a = cls(A)(lambda s: (s, a))
        unit_a.__name__ = str(a)
        return unit_a
    
    @classmethod
    def join(cls, ffa):
        S, A = cls._state_, ffa._value_._value_
        def state_join(s0):
            """
            Flattened stateful computation.
            """
            s1, fa = ffa.run(s0)
            return fa.run(s1)
        return cls(A)(state_join)

    @classmethod
    def gets(cls, f):
        S, A = f.src, f.tgt
        io.asserts.subclass(S, f.src)
        gets_f = cls.unit(Point).gets(f)
        gets_f.__name__ = "gets " + f.__name__
        return gets_f
    
    @classmethod
    def puts(cls, f):
        S, A = f.tgt, f.src
        io.asserts.subclass(A, f.src)

        @Hom(A, cls(A))
        def puts_f(a):
            return cls.unit(Point).puts(f)

        puts_f.__name__ = "puts " + f.__name__
        return puts_f
    
    @classmethod
    def put(cls, s):
        put_s = cls.unit().put(s)
        put_s.__name__ = "put " + str(s)
        return put_s


class State(Hom, metaclass=HomFunctor):

    class _top_(Monad._instance_, Hom._top_): 
        
        def __init__(self, pipe, initial=None):
            self.__name__ = "st"
            super().__init__(pipe)
            self._initial_ = initial

        @property
        def _monad_(self):
            return self._head_(self._state_)
        
        def map(self, f):
            return State(self._state_).fmap(f)(self)
        
        def bind(self, mf):
            maf = super().bind(mf)
            maf.__name__ = self.__name__ + " >> " + mf.__name__
            return maf
        
        def run(self, s=None):
            if s is None:
                s = self._initial_
            return super().__call__(s)
        
        def exec(self, s=None):
            return self.run(s)[0]

        def __call__(self, s=None):
            return self.run(s)[1]
        
        @contextmanager
        def use(self, state):
            try:
                s0 = self._initial_
                self._initial_ = state
                pipe = self._pipe
                s1, a = self.run()
                #self._pipe = (lambda s: (s1, a),)
                yield a
            finally:
                self._pipe = pipe
                self._initial_ = s0
        
        # --- Compositions by method chaining ---

        def then(self, f, tgt=None):
            if tgt is None: 
                tgt = f.tgt
            pipe = (*self._pipe, lambda pair: f(*pair))
            return self._monad_(tgt)(pipe, self._initial_)

        def gets(self, f):
            out = self.then(lambda s, a: (s, f(s)), tgt=f.tgt)
            out.__name__ = self.__name__ + " >> get " + f.__name__
            return out

        def put(self, s):
            out = self.then(lambda *_: (s, ()), tgt=Type.Unit)
            out.__name__ = self.__name__ + " >> put " + str(s)
            return out

        def puts(self, f):
            out = self.then(lambda s, a: (f(a), a), tgt=f.src)
            out.__name__ = self.__name__ + " >> puts " + f.__name__
            return out

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
    def eval(cls, s, f):
        s1, a = super().eval(s, f)
        return a

    @classmethod
    def _subclass_(cls, *xs, **ys):
        print(cls, "_subclass_", xs[:2])
        return Monad.__new__(cls, *xs, **ys)


class Stateful(StateMonad):
    
    _state_ : Type = Var("S")
    _initial_ : Var("S")

    class _top_(State._top_, Hom._top_):
        
        arity = 1
        
        @property
        def _monad_(self):
            return self._head_
        
        def __init__(self, pipe, initial=None):
            super().__init__(pipe, initial)
            if initial is None:
                self._initial_ = type(self)._initial_

        @property
        def state(self):
            return self.run()[0]

        @property
        def value(self):
            return self.run()[1]

    @classmethod
    def new(cls, A):
        name = cls._get_name_(A)
        bases = (cls._top_,)
        dct = dict(
            _value_ = A,
            src = cls._state_,
            tgt = Prod(cls._state_, A),
        )
        SA = Type.__new__(cls, name, bases, dct)
        Type.__init__(SA, name, bases, dct)
        return SA
