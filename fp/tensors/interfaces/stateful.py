import os

from fp.instances import Stateful
from fp import io

from .numpy import NumpyInterface
from .interface import Interface, INTERFACES


class StatefulInterface(Stateful(Interface, NumpyInterface())):

    @classmethod
    def read_env(cls):
        """Set the initial state from $FP_TENSOR_BACKEND.

        Available values are a subset ['numpy', 'jax', 'torch'], depending
        on your environment.
        """
        env = "FP_TENSOR_BACKEND"
        s0 = os.environ[env] if env in os.environ else "torch"
        if s0 in INTERFACES:
            cls._initial_ = INTERFACES[s0]
        else:
            io.log(
                f"Could not find backend {s0}\n"
                "Available backends are: {list(INTERFACES.keys())}"
            )

    @classmethod
    def mock(cls):
        """Return a read-only mock of the Interface state."""
        return cls.get.mock()


StatefulInterface.read_env()
