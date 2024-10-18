from collections import defaultdict
from fp.instances import struct

from .interface import Interface, INTERFACES

import numpy as np


@struct
class NumpyInterface(Interface):

    module = np

    Array = np.ndarray
    asarray = np.asarray

    dtypes = [
        "float:float32",
        "double:float64",
        "int:int32",
        "long:int64",
        "cfloat",
    ]


INTERFACES["numpy"] = NumpyInterface()
