from fp.instances import struct
from .interface import Interface, INTERFACES
from .numpy import NumpyInterface

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

jnp = None if HAS_JAX else jax.numpy
