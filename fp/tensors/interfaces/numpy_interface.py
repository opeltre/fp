from collections import defaultdict
from fp.base import struct

from .interface import Interface, DtypeTable, INTERFACES

import numpy as np


@struct
class NumpyInterface(Interface):

    module = np

    Array = np.ndarray
    asarray = np.asarray
    # dtypes: np.<dtype>(x)
    dtypes = DtypeTable()
    dtypes_bind = "module"


INTERFACES["numpy"] = NumpyInterface()
