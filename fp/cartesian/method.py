import functools
from typing import Callable
from .hom import Hom
from .prod import Prod
from fp.meta import Var


def method(annotated: Callable):
    annotations = annotated.__annotations__
    tgt = annotations.pop("return")
    src_tuple = tuple(annotations.values())
    src = src_tuple[0] if len(src_tuple) == 1 else Prod(*src_tuple)
    signature = lambda T: Hom(src, tgt).substitute({src[0].__name__: T})
    print(signature(Var("A")))
    return Method(signature, annotated)


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
            # (unbound) objtype.<method> : (objtype, *args) -> tgt
            return self.signature(objtype)(self._method)
        elif objtype is not None:
            # (bound) obj.<method> : () -> tgt
            method = self.signature(objtype)(self._method)
            return Hom.partial(method, obj)
        else:
            # (bound) obj.<method> : (*args) -> tgt
            method = self.signature(type(obj))(self._method)
            return Hom.partial(method, obj)
