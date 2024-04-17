from __future__ import annotations

from .kind import Kind
from .type import Type
from .method import Method

import functools

from typing import Callable, Any

import fp.io as io
import fp.utils 


class Constructor(Kind):
    """
    Constructor metaclass. 

    Instances `T` of `Constructor` define a classmethod `T.new(*As)`
    returning a type value `T(*As) = T A1 ... An`. 
    """

    kind = "(*, ...) -> *"
    arity = ...
    
    class _defaults_: 
        
        kind = "(*, ...) -> *"

        @classmethod
        def new(cls, *As: Any):
            try:
                base = cls._top_
                return Type.__new__(cls, 'T As', (base,), {})
                if isinstance(base, Type):
                    return cls('T A', (base,), {})
                return super(Type, cls).__new__(cls, base.__name__, (base,), {})
            except:
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

    def _get_name_(T, *As: Any) -> str:
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
            except:
                # class MyT(T(*As), metaclass=T):
                return super().__new__(cls, *xs, **ys)

        return cached_new

    @staticmethod
    def _new_(T:Constructor, *As: Any) -> Type:
        """
        Wrapper around T.new constructor to be referenced as T.__new__.
        """
        TA = T.new(*As)
        TA.__name__ = T._get_name_(*As)
        T._post_new_(TA, *As)
        TA._head_ = T
        TA._tail_ = As
        return TA
