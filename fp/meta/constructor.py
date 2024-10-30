from __future__ import annotations

import functools
from typing import Callable, Any
from enum import Enum

from colorama import Fore

from .kind import Kind
from .type import Type
from .method import Method

import fp.utils as utils
import fp.utils


class _Mode(Enum):
    new = "new"
    variable = "variable"
    struct = "struct"
    subclass = "subclass"


def _calling_mode(*As, **kwargs) -> _Mode:
    """Check if arguments are unhashable class/struct definitions."""
    # subclass definition calls: T(name, bases, dct)
    if len(As) >= 3 and type(As[2]) is dict:
        return _Mode("subclass")

    # struct definition : Struct(keys, values, name, bases, dct)
    is_struct = len(As) >= 5 and type(As[4]) is dict
    is_struct |= "dct" in kwargs
    if is_struct:
        return _Mode("struct")

    # variable constructor : T.new("A", ...)
    if any(isinstance(A, (str, Var, type(...))) for A in As):
        return _Mode("variable")

    # type constructor : T.new(*As)
    return _Mode("new")


class Constructor(Kind):
    """
    Type constructors.

    Instances define a classmethod `T.new(*As)`
    returning the type value `T(*As) = T A1 ... An`.
    """

    arity = ...

    class _defaults_:

        kind = "(*, ...) -> *"

        @classmethod
        def _pre_new_(cls, *As):
            """
            Parse input variables to a type constructor.

            Defaults to the identity, override to extend support for arguments.
            (e.g. support unhashable inputs, enforce equality of equivalent inputs).
            """
            return As

        @classmethod
        def new(cls, *As: Any):
            try:
                base = cls.Object
                try:
                    name = cls._get_name_(*As)
                except Exception as e:
                    utils.warn(f"Could not compute {cls}._get_name_({As})")
                    name = "T As"
                if isinstance(cls, Type):
                    return type(cls).__new__(cls, name, (base,), {})
                return Type.__new__(cls, name, (base,), {})
            except Exception as e:
                print(e)
                raise RuntimeError(f"Method {cls.__name__}.new was not overriden.")

        @classmethod
        def _subclass_(cls, name: str, bases: tuple, dct: dict):
            msg = str(cls.__name__) + " _subclass_: "
            msg += name + " " + str(bases)
            utils.log(msg, v=1)
            T = Type.__new__(cls, name, bases, dct)
            for base in bases:
                if hasattr(base, "_post_new_"):
                    type(base)._post_new_(T, *base._tail_)
            return T

        def _post_new_(TA, *As):
            """Type initiliazation hook.

            Override this method to configure a newly created type
            without interfering with the metaclass and `new` logic.
            """
            ...

        def __init__(TA, *As): ...

    @property
    def kind(T):
        return "(*, ...) -> *"

    @Method
    def new(T: Constructor):
        return Type.Hom("...", Type)

    def __new__(cls, name, bases, dct):
        """
        Define a new type constructor by wrapping `T.new`.
        """
        T = super().__new__(cls, name, (*bases, cls._defaults_), dct)
        # wrap T.__new__
        T.__new__ = cls._cache_new_(Constructor._new_)
        return T

    def _eval_signature_(T, method) -> Type:
        try:
            sgn = method.signature(T)
            if isinstance(sgn, tuple) and len(sgn) == 2:
                return Type.Hom(*sgn)
            elif isinstance(sgn, tuple):
                return Type.Hom(sgn[:-1], sgn[-1])
            return sgn
        except:
            return super()._eval_signature_(method)

    def _get_name_(T, *As: Any) -> str:
        """
        String representation of output type.
        """
        get_name = lambda A: A.__name__ if hasattr(A, "__name__") else str(A)
        if len(As) > 1:
            tail = "(" + ", ".join(get_name(A) for A in As) + ")"
        elif len(As) == 1:
            tail = get_name(As[0])
        else:
            tail = ""
        return T.__name__ + " " + tail

    @classmethod
    def _cache_new_(cls, new: Callable) -> Callable:
        """
        Cached `Constructor.__new__`, compatible with subclass definitions.
        """
        new_ = functools.cache(new)

        def cached_new(cls, *xs, **ys):
            mode = _calling_mode(*xs, **ys)
            if mode == _Mode("new") or mode == _Mode("variable"):
                # T(*As)
                xs = cls._pre_new_(*xs)
                return new_(cls, *xs, **ys)
            elif mode == _Mode("subclass") or mode == _Mode("struct"):
                # class MyT(T(*As), metaclass=T):
                return new(cls, *xs, **ys)

        return cached_new

    @staticmethod
    def _new_(T: Constructor, *As: Any) -> Type:
        """Defines `T.__new__` as a wrapper around `T.new`."""
        mode = _calling_mode(*As)
        if mode == _Mode("subclass"):
            try:
                utils.log(f"Subclass {As[0]} -> {T}", v=2)
                if hasattr(T, "_subclass_") and mode.name == "subclass":
                    return T._subclass_(*As[:3])
                TA = Type.__new__(T, *As)
                base = As[1][0]
                TA._head_ = base._head_
                TA._tail_ = base._tail_
                return TA
            except Exception as err:
                print(err)
                raise utils.ConstructorError(
                    f"Could not create subclass {As[0]} of {T}.\n\n"
                    "If you override T._subclass_(name, bases, dct), "
                    "it must return a type."
                )

        if mode == _Mode("variable"):
            try:
                utils.log(f"Parameterised type: {T}({As})", v=2)
                if T is not Var:
                    As = Var._read_vars_(As)
                elif T is Var:
                    As = tuple(A if A is not ... else "..." for A in As)
                if issubclass(T, Var):
                    TA = T.new(*(A if A is not ... else "..." for A in As))
                else:
                    TA = T.var()(*As)

            except Exception as err:
                raise utils.ConstructorError(
                    f"Could not create parameterised type {T}({As})"
                )

        if mode == _Mode("new"):
            utils.log(f"Concrete type: {T}({As})", v=2)
            TA = T.new(*As)

        if mode == _Mode("struct"):
            utils.log(f"Struct type: {As[:2]}", v=2)
            TA = T.new(*As)

        # post new
        TA.__name__ = T._get_name_(*As)
        TA._head_ = T
        TA._tail_ = As
        T._post_new_(TA, *As)
        return TA

    def var(T) -> Constructor:
        """
        Return constructor instance acting on type variables.
        """

        class VarT(T, Var, metaclass=T.__class__):

            src = Type
            tgt = Var

            def _post_new_(A, *xs, **ys): ...

        def _check_methods_(self, T, bases, dct):
            """
            Check that declared class methods are defined.

            Called by `Kind.__new__` to explicitly call setattr as needed.
            """
            ...

        VarT.__name__ = T.__name__
        return VarT


# --- Type variables ---


class Var(Type, metaclass=Constructor):

    _accessors_ = None

    class Object: ...

    @classmethod
    def new(cls, *As):
        return super().new(*As)

    def _post_new_(A, name: str, *accessors: str):
        A._tail_ = None
        A._accessors_ = accessors

    def __getattr__(A, k):
        Ak = Var.__new__(Var, A.__name__, k)
        return Ak

    def match(A, B):
        """Matches `{"Ai": Type}` against a concrete type B."""
        # --- leaf node ---
        if A._tail_ is None:
            return {A.__name__: B}
        if not "_head_" in dir(B):
            return None

        out = {}
        # --- head of expression ---
        if isinstance(A._head_, Var):
            name = A._head_.__name__
            out[name] = B._head_

        # --- tail of expression ---

        nA, nB = len(A._tail_), len(B._tail_)
        n = 1 + nB - nA

        # Ellipsis
        dots = Var("...")
        if nA == nB:
            tail = A._tail_
        elif dots == A._tail_[-1] and n >= 0:
            ndots = [dots] * n
            tail = (*A._tail_[:-1], *ndots)
        elif dots == A._tail_[0] and n >= 0:
            ndots = [dots] * n
            tail = (*ndots, *A._tail_[1:])
        else:
            return None

        # Recursive matching on leaves
        dots, dotsname = [], "..."
        for Ai, Bi in zip(tail, B._tail_):
            if isinstance(Ai, Var):
                mi = Var.match(Ai, Bi)
                if mi == None:
                    return None
                elif Ai.__name__ == "...":
                    dots.append(Bi)
                elif Ai.__name__ not in out:
                    out |= mi
                elif out[Ai.__name__] != Bi:
                    return None
            elif Ai != Bi:
                return None
        while dotsname in out:
            dotsname += "."
        out[dotsname] = tuple(dots)
        return out

    def substitute(A, matches: dict[str, Type]) -> Type:
        """
        Concrete type obtained by substitution of matches.
        """
        if A._tail_ is None:
            name = A.__name__.split(":")[0]
            SA = matches[name]
            if not A._accessors_ and isinstance(SA, Type):
                return SA
            if A._accessors_ and isinstance(SA, Type):
                for attr in A._accessors_:
                    SA = getattr(SA, attr)
                return SA
            elif isinstance(SA, tuple):
                return tuple(A.substitute({name: Si}) for Si in SA)
        head = A._head_ if not isinstance(A._head_, Var) else matches[A._head_.__name__]
        tail = []
        for Ai in A._tail_:
            if isinstance(Ai, Var):
                Si = Ai.substitute(matches)
                if isinstance(Si, Type):
                    tail.append(Si)
                elif isinstance(Si, tuple):
                    tail.append(*Si)
            else:
                tail.append(Ai)
        return head(*tail)

    @classmethod
    def _get_name_(cls, name: str, *accessors: str) -> str:
        name = name if isinstance(name, str) else str(name)
        for a in accessors:
            name += ":" + a
        return name

    @classmethod
    def _read_var_(cls, A):
        """
        Look for a type variable input, parsing `str` and `Ellipsis`.
        """
        if isinstance(A, str):
            return Var(A)
        elif A is ...:
            return Var("...")
        return A

    @classmethod
    def _read_vars_(cls, As: tuple[type, ...]):
        return tuple(cls._read_var_(A) for A in As)

    @classmethod
    def cast(cls, x):
        return x


class Ellipsis(Var):

    def substitute(A, matches): ...
