from __future__ import annotations
import typing 

from fp.meta import Cofunctor, Var
from fp.cartesian import Type, Prod, Hom, Arrow
from .list import List
from .str import Str

import fp.io as io
from fp.io.show import showStruct

class Key(List(Str)):
    
    Hom = Arrow


class Field:
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
    def __init__(self, slot_descriptor, V, v=None):
        self.slot_descriptor = slot_descriptor
        self._value_ = V
        if v is not None:
            self._default_ = v
    
    @classmethod
    def bind(cls, src:tuple[Type, str], tgt: Type | Value):
        """
        Bind a named accessor to the source `Struct` type.
        """
        S, k = src
        V, *v = tgt if isinstance(tgt, tuple) else (tgt, ())
        slot = getattr(S, k)
        field = cls(slot, V, *v)
        field.__set_name__(k, S)
        setattr(S, k, field)
        return field

    def __set_name__(self, name, objtype):
        self._key_ = name

    def __get__(self, obj, objtype=None):
        if obj is not None:
            return self.slot_descriptor.__get__(obj, objtype)
        # typed class method
        src, tgt = objtype, self._value_
        get = Hom(src, tgt)(lambda obj: self.slot_descriptor.__get__(obj))
        get.__name__ = "." + self._key_
        return get

    def __set__(self, obj, val):
        self.slot_descriptor.__set__(obj, val)

    def _with_(self, obj, val):
        out = obj.copy()
        self.__set__(out, val)
        return out




class StructObject(metaclass=Type):
    """
    Base class for `Struct` objects.
    
    The empty struct is the pullback of any child instance by 
    the universal inclusion `() -> D` for any domain `D : tuple[keys]`. 
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
            setattr(self, name, io.cast(x, Tx))
        for name, Tx, *val in fields[nargs:]:
            try:
                y = ys[name]
                setattr(self, name, io.cast(y, Tx))
            except: 
                if len(val):
                    y, = val
                    setattr(self, name, io.cast(y, Tx))
                else:
                    struct = self.__class__
                    raise io.KeyError(
                        f"Missing key {name} creating a {struct} instance."
                    )
    
    def __len__(self):
        return len(self.__slots__)
    
    def __iter__(self):
        for k in self.__slots__:
            yield k
    
    def keys(self):
        return self.__slots__
    
    def items(self):
        for k in self:
            yield k, getattr(self, k)

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
    
    def pull(self, keys):
        if isinstance(keys, tuple):
            xs = (getattr(self, k) for k in keys)
            values = tuple((type(x), x) for x in xs)
            return Struct(keys, values)(*xs)

    def map(self, **fs):
        targets = []
        ys = []
        defaults = []
        for key, (src, *deft) in zip(self._keys_, self._values_):
            x = getattr(self, key)
            if key in fs:
                f = fs[key]
                if type(f) is tuple:
                    f, tgt = f
                else:
                    tgt = hasattr(f, 'tgt') and f.tgt
                y = f(x)
                ys.append(y)
                targets.append(tgt or type(y))
                defaults.append(deft if tgt is src else ())
        fields = (
            (k, Ty, *y) for k, Ty, y in zip(self.__slots__, targets, defaults)
        )
        return self._head_(*fields)(*ys)

    def apply(self, **fs):
        for key, f in fs.items():
            x = getattr(self, key)
            setattr(self, key, f(x))

# alias for pointed types (T, val:T)
Value = tuple[Type, typing.Any]

class Struct(Type, metaclass=Cofunctor):
    
    src = Key
    tgt = Type 
    
    Object = StructObject

    @classmethod
    def _pre_new_(cls, 
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
    def new(cls, 
            keys: tuple[str], 
            values: Type|tuple[Type|Value]=(),
            name : (str | None) = None,
            bases : tuple[type, ...] = (),
            dct : dict = {},
        ) -> Struct:
        """
        Return a new `Struct` type. 
        """
        if isinstance(values, Type):
            values = tuple([values] * len(keys))
        values = tuple((*v,) if type(v) is tuple else v for v in values)
        dct = dct | dict(
            __slots__ = keys,
            _keys_ = keys,
            _values_ = values
        )
        if name is None:
            name = cls._get_name_(keys, values, name, bases)
        if StructObject not in bases:
            bases = (*bases, StructObject)
        return super(Type, cls).__new__(cls, name, bases, dct)
    
    def _post_new_(S, keys, values, name = None, bases = (), dct=None):
        for k, (V, *v) in zip(keys, values):
            Field.bind((S, k), (V, *v))

    @classmethod
    def _annotations_(cls, C):
        # context-specific getter (subclass, decorator)
        get = (C.__getitem__ if isinstance(C, dict)
               else lambda k: getattr(C, k))
        # accumulate fieldnames, types, and default values
        keys, values = [], []
        for k, Tk in get('__annotations__').items():
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
        ...

def struct(C : type) -> Struct:
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
