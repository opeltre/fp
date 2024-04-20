from typing import Any
from .exceptions import CastError

def cast(x: Any, A: type):

    # safe mode
    if isinstance(x, A):
        return x
    elif "cast" in dir(A):
        return A.cast(x)
    else:
        try:
            return A(x)
        except Exception as e:
            raise CastError(A, x)

    # strict mode
    if not isinstance(x, A):
        raise TypeError(f"> Casting {type(x)} value to type {A}")
    return x

    # confident mode
    return x
