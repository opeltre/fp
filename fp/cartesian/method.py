import functools
from typing import Callable
from .hom import Hom


class Method:

    @classmethod
    def annotate(cls, signature):
        return lambda method: cls(signature, method)

    def __init__(self, signature: Callable[type, Hom], method=None):
        self.signature = signature
        self._method = method

    def __set_name__(self, objtype, name):
        self.__name__ = name

    def __get__(self, obj, objtype=None) -> Hom.Object:
        if obj is None:
            return self.signature(objtype)(self._method)
        elif objtype is not None:
            method = self.signature(objtype)(self._method)
            return Hom.partial(method, obj)
        else:
            method = self.signature(type(obj))(self._method)
            return Hom.partial(method, obj)
