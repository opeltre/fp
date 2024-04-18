from __future__ import annotations

from .kind import Kind
from .type import Type
from .method import Method

import functools

from typing import Callable, Any

import fp.io as io
import fp.utils 

from colorama import Fore

class Constructor(Kind):
    """
    Type constructors.

    Instances define a classmethod `T.new(*As)`
    returning the type value `T(*As) = T A1 ... An`. 
    """

    kind = "(*, ...) -> *"
    arity = ...
    
    class _defaults_ : 
        
        kind = "(*, ...) -> *"

        @classmethod
        def new(cls, *As: Any):
            try:
                base = cls._top_
                if isinstance(cls, Type):
                    print("__new__ from type cls: ", type(cls))
                    return type(cls).__new__(cls, 'T A', (base,), {})
                return Type.__new__(cls, 'T As', (base,), {})
            except Exception as e:
                print(e)
                raise RuntimeError(f"Method {cls.__name__}.new was not overriden.")

        def _post_new_(TA, *As):
            ...

        def __init__(TA, *As):
            ...

    @Method 
    def new(T: Constructor):
        return ..., type 

    def __new__(cls, name, bases, dct):
        """
        Define a new type constructor by wrapping `T.new`.
        """
        T = super().__new__(cls, name, (*bases, cls._defaults_), dct)
        # wrap T.__new__
        T.__new__ = cls._cache_new_(Constructor._new_)
        return T
    
    def _get_name_(T , *As: Any) -> str:
        """
        String representation of output type.
        """
        get_name = lambda A: A.__name__ if hasattr(A, '__name__') else str(A)
        if len(As) > 1:
            tail = '(' + ', '.join(get_name(A) for A in As) + ')'
        elif len(As) == 1: 
            tail = get_name(As[0])
        else: 
            tail = ''
        return T.__name__ + ' ' + tail
    
    @classmethod
    def _cache_new_(cls, new : Callable) -> Callable:
        """
        Cached `Constructor.__new__`, compatible with subclass definitions.
        """
        new_ = functools.cache(new)
        def cached_new(cls, *xs, **ys):
            try: 
                # T(*As)
                return new_(cls, *xs, **ys)
            except Exception as e:
                # class MyT(T(*As), metaclass=T):
                return new(cls, *xs, **ys)
                raise e

        return cached_new

    @staticmethod
    def _new_(T:Constructor, *As: Any) -> Type:
        """
        Wrapper around T.new constructor to be referenced as T.__new__.
        """
        try:
            if any(isinstance(A, (str, Var)) for A in As):
                if len(As) >= 3 and isinstance(As[2], dict):
                    raise RuntimeError("")
                Bs = []
                if T is not Var:
                    As = tuple(Var(A) if isinstance(A, str) else A for A in As)
                if issubclass(T, Var):
                    print("Var T A")
                    TA = T.new(*Bs)
                else:
                    print("T.var(*As)")
                    TA = T.var(T.__name__).new(*Bs)
            else:
                TA = T.new(*As)
            TA.__name__ = T._get_name_(*As)
            TA._head_ = T
            TA._tail_ = As
            T._post_new_(TA, *As)
            return TA
        except Exception as e:
            TA = Type.__new__(T, *As)
            base = As[1][0]
            TA._head_ = base._head_
            TA._tail_ = base._tail_
            return TA
        except:
            raise io.ConstructorError("new", T, As)
        
    @classmethod
    def var(cls, name="T") -> str:
        """
        Return constructor instance acting on type variables.
        """
        class VarT(Var, metaclass=cls):

            src = Type
            tgt = Var

        VarT.__name__ = name
        return VarT


# --- Type variables ---

class Var(Type, metaclass=Constructor):
    
    class _top_:

        def __repr__(self):
            return Fore.GREEN + self.__name__ + Fore.RESET

        def __str__(self):
            return Fore.YELLOW + self.__name__ + Fore.RESET

    def __init__(A, name, head=None, tail=None):
        if A._tail_ == (A.__name__,):
            A._tail_ = None

    def match(A, B):
        """Matches `{"Ai": Type}` against a concrete type B."""
        print("match A:", A, "\tB:", B) 
        # --- leaf node ---
        if A._tail_ == None:
            return {A.__name__: B}
        if not "_head_" in dir(B):
            print("no head!")
            return None

        out = {}
        # --- head of expression ---
        if isinstance(A._head_, Var): 
            out[A._head_.__name__] = B._head_

        # --- tail of expression
        if len(A._tail_) == len(B._tail_):
            for Ai, Bi in zip(A._tail_, B._tail_):
                print("match Ai:", Ai, "\tBi:", Bi)
                if isinstance(Ai, Var):
                    mi = Var.match(Ai, Bi)
                    if mi == None:
                        return None
                    elif Ai.__name__ not in out:
                        out |= mi
                    elif out[Ai.__name__] != Bi:
                        return None
                elif Ai != Bi:
                    return None
            return out
        return None
    
    @classmethod
    def _get_name_(cls, name, *xs, **ys):
        return name

    def substitute(A, matches):
        """Return concrete type obtained by substitution of matches."""
        if A._tail_ == None:
            return matches[A.__name__]
        head = (
            A._head_ if not isinstance(A._head_, Var) else matches[A._head_.__name__]
        )
        tail = []
        for Ai in A._tail_:
            tail.append(Ai.substitute(matches) if isinstance(Ai, Var) else Ai)
        return head(*tail)
