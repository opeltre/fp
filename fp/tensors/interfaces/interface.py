import numpy as np

from types import ModuleType
from typing import Callable
from fp.instances import struct, List, Str

# ====== Interfaces : populated during __init__.py ======

INTERFACES = {}


@struct
class Interface:
    """Declares bindings to a numerical backend.

    `Interface` objects can be mapped to a `TensorBase <= Ring` subclass, by
    any functor wrapping over the `interface.Array` type.
    See :class:`Backend` for such a functor.

    The summarized `struct` layout makes it easier to spot and enumerate what
    are mere naming differences.

    Args:
        module (ModuleType): python module
        Array (type): base array class, e.g. `np.ndarray`
        asarray (callable): default constructor
        dtypes (list[str]): list of dtypes, optionally prepended by alias + `:`, e.g.
            `"float:float32"`
        repeat (str): name of `"repeat"` method (`"repeat_interleave"` for torch)
        tile (str): name of `"tile"` method (`"repeat"` for torch)
    """

    module: ModuleType
    Array: type
    asarray: Callable
    dtypes: List(Str)
    # aliases
    repeat: Str = "repeat"
    tile: Str = "tile"

    def __repr__(self):
        return self.module.__name__

    def __str__(self):
        return self.module.__name__
