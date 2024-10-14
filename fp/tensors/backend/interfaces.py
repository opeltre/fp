from collections import defaultdict
from fp.instances import struct

from .wrap_alg import Backend, Interface
from types import ModuleType

import numpy as np

INTERFACES = {}


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

# --- jax ---

try:
    import jax

    HAS_JAX = True

    @struct
    class JaxInterface(Interface):

        module = jax.numpy
        Array = jax.lib.xla_extension.ArrayImpl
        asarray = jax.numpy.asarray

        dtypes = NumpyInterface().dtypes[:-1] + [
            "cfloat:complex64",
            "cdouble:complex128",
        ]

    INTERFACES["jax"] = JaxInterface()

except ModuleNotFoundError:
    jax = None
    HAS_JAX = False

jnp = None if jax is None else jax.numpy

# --- torch ---

try:
    import torch

    HAS_TORCH = True

    @struct
    class TorchInterface(Interface):

        module = torch

        Array = torch.Tensor
        asarray = torch.as_tensor

        # dtypes
        dtypes = [
            "float",
            "double",
            "int",
            "long",
            "cfloat",
        ]

        repeat = "repeat_interleave"
        tile = "repeat"

    INTERFACES["torch"] = TorchInterface()

except ModuleNotFoundError:
    torch = None
    HAS_TORCH = False

torch_interface = TorchInterface() if HAS_TORCH else NumpyInterface()


"""
class Backend(Stateful(Interface, NumpyInterface())):
    
    @classmethod
    def read_env(cls) -> str:
        env = "FP_BACKEND"
        s0 = os.environ[env] if env in os.environ else "torch"
"""
