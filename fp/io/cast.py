from typing import Any


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
            print(f"> Casting {type(x)} value to type {A}")
            raise e

    # strict mode
    if not isinstance(x, A):
        raise TypeError(f"> Casting {type(x)} value to type {A}")
    return x

    # confident mode
    return x
