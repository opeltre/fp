from __future__ import annotations
import typing

from fp.meta import Cofunctor, Var
from fp.cartesian import Type, Prod, Hom, Arrow
from .list import List
from .str import Str

import fp.utils as utils
from fp.utils.show import showStruct


class Key(List(Str)):
    """Category of keys, partial order for inclusion."""

    Hom = Arrow


class FieldObject(Hom.Object):
    """Field descriptors."""

    def __init__(self, slot_descriptor, key: str):
        getter = lambda obj: slot_descriptor.__get__(obj)
        super().__init__(getter)
        self._slot_descriptor = slot_descriptor
        self._key_ = key
        self._value_ = self.tgt
        self.__name__ = "." + key

    def __get__(self, obj, objtype=None):
        if obj is not None:
            return self._slot_descriptor.__get__(obj, objtype)
        # typed class method
        src, tgt = objtype, self._value_
        get = Field(src, tgt)(self._slot_descriptor, self._key_)
        get.__name__ = "." + self._key_
        return get

    def __set__(self, obj, val):
        self._slot_descriptor.__set__(obj, val)

    @property
    def set(self):
        """Pure field update."""
        S, T = self.src, self.tgt

        @Hom((T, S), S)
        def setter(value, obj):
            copy = S(**obj)
            self._slot_descriptor.__set__(copy, value)
            return copy

        setter.__name__ = self.__name__ + ".set"
        return setter

    @property
    def put(self):
        """In-place field update."""
        S, T = self.src, self.tgt

        @Hom((T, S), S)
        def putter(value, obj):
            self._slot_descriptor.__set__(obj, value)
            return obj

        putter.__name__ = self.__name__ + ".put"
        return putter


class Field(Hom):
    """
    Manage `Struct` access and updates.

        # getter
        Struct.field : Struct -> V
        # setter
        Struct.field.put : V -> Struct -> Struct
        # pure update
        Struct.field.set : V -> Struct -> Struct

        # field value
        obj.field : V
    """

    Object = FieldObject

    @classmethod
    def bind(cls, src: tuple[Type, str], tgt: Type | Value):
        """
        Bind a named accessor to the source `Struct` type.
        """
        S, k = src
        V, *v = tgt if isinstance(tgt, tuple) else (tgt, ())
        slot = getattr(S, k)
        field = cls(S, V)(slot, k)
        field.__set_name__(k, S)
        setattr(S, k, field)
        return field


class StructObject(metaclass=Type):
    """Base class for `Struct` objects.

    Structs are mutable and use slot-based attribute management, which means
    they cannot be assigned any new attribute that is not contained in their
    type's keys.
    """

    __slots__ = ()

    def __init__(self, *xs, **ys):
        """
        Initialize fields.
        """
        super().__init__()
        nargs = len(xs)
        fields = [(k, *v) for k, v in zip(self._keys_, self._values_)]
        for x, (name, Tx, *_) in zip(xs, fields):
            setattr(self, name, utils.cast(x, Tx))
        for name, Tx, *val in fields[nargs:]:
            try:
                y = ys[name]
                setattr(self, name, utils.cast(y, Tx))
            except:
                if len(val):
                    (y,) = val
                    setattr(self, name, utils.cast(y, Tx))
                else:
                    struct = self.__class__
                    raise utils.KeyError(
                        f"Missing key {name} creating a {struct} instance."
                    )

    def __len__(self):
        return len(self.__slots__)

    def __iter__(self):
        for k in self.__slots__:
            yield k

    def values(self):
        for k, v in self.items():
            yield v

    def keys(self):
        return self.__slots__

    def items(self):
        for k in self:
            yield k, getattr(self, k)

    def __eq__(self, other):
        if type(other) != type(self):
            return False
        return all(x == y for x, y in zip(self.values(), other.values()))

    def __hash__(self):
        return id(self)

    def __getitem__(self, k):
        if isinstance(k, int):
            return getattr(self, self.__slots__[k])
        if isinstance(k, slice):
            return self.pull(*self.__slots__[k])
        if isinstance(k, str):
            return getattr(self, k)

    def __str__(self):
        return showStruct(self)

    def __repr__(self):
        return showStruct(self)

    def pull(self, Super: Type):
        xs = (getattr(self, k) for k in Super._keys_)
        return Super(*xs)


# alias for pointed types (T, val:T)
Value = tuple[Type, typing.Any]


class Struct(Type, metaclass=Cofunctor):
    """Struct functor, contravariant in the set of keys."""

    src = Key
    tgt = Type

    Object = StructObject

    @classmethod
    def _pre_new_(
        cls,
        keys: tuple[str, ...],
        values: tuple[Value, ...] = (),
        name: typing.Optional[str] = None,
        bases: tuple[type, ...] = (),
        dct: typing.Optional[dict] = None,
    ):
        ###
        if type(keys) is str and type(name) is dict:
            return keys, values, name, bases
        ###
        if isinstance(keys, (Var, str)):
            keys = ("k0", "k1")
            values = ("V0", "V1")
        if isinstance(bases, tuple) and dct is not None:
            return tuple(keys), tuple(values), None, bases, dct
        elif isinstance(bases, tuple):
            return tuple(keys), tuple(values), None, bases
        return tuple(keys), tuple(values)

    @classmethod
    def new(
        cls,
        keys: tuple[str, ...],
        values: tuple[Type | Value, ...] = (),
        name: str | None = None,
        bases: tuple[type, ...] = (),
        dct: dict = {},
    ) -> Struct:
        """
        Return a new `Struct` type.
        """
        if isinstance(values, Type):
            values = tuple([values] * len(keys))
        values = tuple((*v,) if type(v) is tuple else v for v in values)
        dct = dct | dict(__slots__=keys, _keys_=keys, _values_=values)
        if name is None:
            name = cls._get_name_(keys, values, name, bases)
        if StructObject not in bases:
            bases = (*bases, StructObject)
        return super(Type, cls).__new__(cls, name, bases, dct)

    def _post_new_(S, keys, values, name=None, bases=(), dct=None):
        for k, (V, *v) in zip(keys, values):
            Field.bind((S, k), (V, *v))

    @classmethod
    def _annotations_(cls, C):
        # context-specific getter (subclass, decorator)
        get = C.__getitem__ if isinstance(C, dict) else lambda k: getattr(C, k)
        # accumulate fieldnames, types, and default values
        keys, values = [], []
        for k, Tk in get("__annotations__").items():
            keys.append(k)
            try:
                vk = (Tk, get(k))
            except:
                vk = (Tk,)
            values.append(vk)
        return tuple(keys), tuple(values)

    @classmethod
    def _get_name_(cls, keys, values=(), name=None, bases=(), dct=None):
        if name is not None:
            return name
        return "Struct *"

    @classmethod
    def _subclass_(cls, name, bases, dct):
        Sgn = {}
        for b in bases[::-1]:
            if isinstance(b, Struct):
                Sgn |= {k: v for k, v in zip(b._keys_, b._values_)}
        if not "__annotations__" in dct:
            dct["__annotations__"] = {k: Sgn[k][0] for k in Sgn if k in dct}
        keys, values = cls._annotations_(dct)
        Sgn |= {k: v for k, v in zip(keys, values)}
        keys, values = tuple(Sgn.keys()), tuple(Sgn.values())
        for k in keys:
            try:
                del dct[k]
            except:
                ...
        S = cls.new(keys, values, name, bases, dct)
        S.__name__ = name
        S._post_new_(keys, values)
        return S

    def __iter__(S):
        for k in S._keys_:
            yield k

    def items(S):
        for k, (V, *v) in zip(S._keys_, S._values_):
            yield k, V

    def __getitem__(S, k):
        # k-th projection
        if isinstance(k, int):
            V, *v = S._values_[k]
            return V
        # sliced product type
        if isinstance(k, slice):
            Vs = (V for V, *_ in S._values_[k])
            return Prod(*Vs)
        # type of named field (S.field.tgt)
        if isinstance(k, str):
            return getattr(S, k).tgt
        # pulled super type
        if isinstance(k, tuple):
            values = tuple(S[key].tgt for key in k)
            return values

    @classmethod
    def cofmap(cls, f):
        """Pullback, i.e. restriction to a subset of keys."""
        raise NotImplementedError(
            "TODO: construct a struct 'supertype' given any Key.Hom arrow.\n"
            "If this arrow has a name and is hashable, we may be able "
            "to return the same supertype every time.\n\n"
            "It is of course better practice to effectively define the supertype "
            "before hand and inherit from it, using `.pull` to extract subfields."
        )


def struct(C: type) -> Struct:
    """
    Decorator definition of `Struct` types (dataclass-like).
    """
    if isinstance(C, Struct):
        return C
    keys, values = Struct._annotations_(C)
    bases = (C,)
    dct = dict(C.__dict__)
    del dct["__dict__"]
    for k in keys:
        if k in dct:
            del dct[k]
    S = Struct(keys, values, C.__name__, (), dct)
    S.__name__ = C.__name__
    return S
