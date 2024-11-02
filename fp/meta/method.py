from __future__ import annotations

import functools
from typing import Callable
from .type import Type
from .constructor import Var
from fp.utils.exceptions import SignatureError


def _read_method_signature(annotated: Callable):
    """Parse method signature, with first type variable substitution."""
    annotations = annotated.__annotations__
    tgt = annotations.pop("return")
    src_tuple = tuple(annotations.values())
    src0 = src_tuple[0]
    src = src0 if len(src_tuple) == 1 else Type.Prod(*src_tuple)
    signature = lambda T: Type.Hom(src, tgt).substitute({src0.__name__: T})
    # Preventively evaluate signature upon method definition
    try:
        signature_T = signature(Var("T"))
    except:
        raise SignatureError(
            f"Could not read signature from annotations: {annotations}\n\n"
            "Make sure you annotated all variables, or use `Method.annotate` "
            "to pass `signature : type -> Hom` explicitly."
        )
    return signature


class Method:

    @classmethod
    def annotate(cls, signature):
        return lambda method: cls(method, signature)

    def __init__(
        self, method: Callable, signature: Callable[type, Type.Hom] | None = None
    ):
        if signature is None:
            # infer signature from annotations
            signature = _read_method_signature(method)
        self.signature = signature
        self._method = method

    def __set_name__(self, objtype, name):
        self.__name__ = name

    def __get__(self, obj, objtype=None) -> Type.Hom.Object:
        if obj is None:
            # (unbound) objtype.<method> : (objtype, *args) -> tgt
            return self.signature(objtype)(self._method)
        elif objtype is not None:
            # (bound) obj.<method> : () -> tgt
            method = self.signature(objtype)(self._method)
            return Type.Hom.partial(method, obj)
        else:
            # (bound) obj.<method> : (*args) -> tgt
            method = self.signature(type(obj))(self._method)
            return Type.Hom.partial(method, obj)


class ClassMethod(Method):

    def __init__(
        self, method: Callable, signature: Callable[type, Type.Hom] | None = None
    ):
        if signature is None:
            try:
                # infer signature from annotations
                signature = _read_method_signature(method)
            except:
                ...
        self.signature = signature
        self._method = method

    def __set_name__(self, objtype, name):
        self.__name__ = name
        if hasattr(objtype, "method_signatures"):
            signatures = objtype.method_signatures()
            if name in signatures:
                signature = signatures[name]
                self.signature = signature

    def __get__(self, obj, objtype=None) -> Type.Hom.Object:
        if self.signature is None:
            # _defaults_ has no signatures:
            # they are manually set by Kind.__init_subclass__ for now
            return self
        if objtype is None:
            objtype = type(obj)
        method_cls = functools.partial(self._method, objtype)
        method_cls.__name__ = objtype.__name__ + "." + self._method.__name__
        homtype = self.signature(objtype)
        if isinstance(homtype, tuple):
            # most TypeClassMethod signatures return tuple
            homtype = Type.Hom(*homtype)
        return homtype(method_cls)
