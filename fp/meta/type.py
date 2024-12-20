from .kind import Kind
import fp.utils as utils
import fp

from typing import Any


class Type(type, metaclass=Kind):
    """
    Type Category.

    All types within `fp` are instances of `Type`,
    while type classes subclass `Type`.

    Example:
    --------
    .. code::

        >>> isinstance(Int, Type) and isinstance(List(Int), Type)
        True
        >>> issubclass(List, Type)
        True
        >>> issubclass(Ring, Type)
        True
    """

    def __new__(cls, name, bases=(), dct={}, head=None, tail=None):
        """Create a new type expression."""
        if isinstance(name, type):
            return cls._from_class_definition(name)
        T = super().__new__(cls, name, bases, dct)
        # expression tree for pattern matching
        T._head_ = name if isinstance(head, type(None)) else head
        T._tail_ = tail
        # pretty print type annotations
        T.__str__ = utils.str_method(T.__str__)
        T.__repr__ = utils.repr_method(T.__repr__)

        # seamless printing helpers
        def shows(x: Any, m: str) -> Any:
            """
            Print a value x and set its name, returning x.
            """
            x.__name__ = m
            print(">>> " + m, repr(x), sep="\n")
            return x

        def show(x: Any) -> Any:
            """
            Print x, prefixed by its name if any, and return x.
            """
            if hasattr(x, "__name__"):
                print(">>> " + x.__name__)
            print(repr(x))
            return x

        T.shows = shows
        T.show = show
        return T

    @classmethod
    def _from_class_definition(cls, class_def: type) -> type:
        # decorate a class definition
        return cls.__new__(
            cls,
            class_def.__name__,
            class_def.__bases__,
            dict(class_def.__dict__),
        )

    def __init__(self, *xs, **ys): ...

    def __repr__(self):
        """Show type name."""
        return f"{self.__name__}"

    def __pow__(self, other):
        return self.__class__.Hom(other, self)

    def __rshift__(self, other):
        return self.__class__.Hom(self, other)

    def __mul__(self, other):
        return self.__class__.Prod(self, other)

    def __or__(self, other):
        return self.__class__.Sum(self, other)
