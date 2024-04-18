from .kind import Kind
import fp.io as io

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
        T = super().__new__(cls, name, bases, dct)
        # expression tree for pattern matching 
        T._head_ = name if isinstance(head, type(None)) else head
        T._tail_ = tail
        # pretty print type annotations
        T.__str__ = io.str_method(T.__str__)
        T.__repr__ = io.repr_method(T.__repr__)

        def shows(x:Any, m:str) -> Any:
            x.__name__ = m
            print(">>> " + m, repr(x), sep=":\n") 
            return x

        T.shows = shows
        return T
    
    def __repr__(self):
        """Show type name."""
        return f"{self.__name__}"
