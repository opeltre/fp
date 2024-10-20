from fp.instances import struct
from .interface import Interface, DtypeTable, INTERFACES
from .numpy_interface import NumpyInterface

try:
    import jax

    HAS_JAX = True

    @struct
    class JaxInterface(Interface):
        module = jax.numpy
        # array class and constructor
        Array = jax.lib.xla_extension.ArrayImpl
        asarray = jax.numpy.asarray
        # dtypes : jax.numpy.<dtype>(x)
        dtypes = DtypeTable()
        dtypes_bind = "module"

    INTERFACES["jax"] = JaxInterface()

except ModuleNotFoundError:
    jax = None
    HAS_JAX = False

jnp = None if HAS_JAX else jax.numpy
