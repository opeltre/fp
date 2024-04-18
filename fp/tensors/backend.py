import pkg_resources
import os

import typing
from typing import TypeAlias, Union, Any, Callable, Dict, Iterable

import numpy as np

# --- Get available backends ---

pkgs = [p.project_name for p in pkg_resources.working_set]

has_jax = "jax" in pkgs
has_torch = "torch" in pkgs

del pkgs

# --- Export references ---

if has_jax:
    import jax
else:
    jax = False

if has_torch:
    import torch
else:
    torch = False

# --- Interface for helpers  ---


class ArrayInterface:
    module: Any = None
    Array: TypeAlias = type(None)
    asarray: typing.Callable = lambda x: x
    Device: TypeAlias = str


class NumpyInterface(ArrayInterface):
    module: Any = np
    Array: TypeAlias = np.ndarray
    asarray: Callable[Any, np.ndarray] = np.asarray
    Device: TypeAlias = str

    @classmethod
    def device_put(x: np.ndarray, device: str = "cpu"):
        return x


if has_torch:

    class TorchInterface(ArrayInterface):
        module: Any = torch
        Array: TypeAlias = torch.Tensor
        asarray: Callable[Any, torch.Tensor] = torch.as_tensor
        Device: TypeAlias = torch.device

        @classmethod
        def device_put(x: torch.Tensor, device: torch.device):
            return x.to(device)


if has_jax:

    class JaxInterface(ArrayInterface):
        module: Any = jax
        Array: TypeAlias = jax.Array
        asarray: Callable[Any, jax.Array] = jax.numpy.asarray
        Device: TypeAlias = jax.Device

        @classmethod
        def device_put(x: jax.Array, device: jax.Device):
            return jax.device_put(x, device)


# --- Array Types ---

AVAILABLE = {}
for name, available, Interface in zip(
    ("np", "torch", "jax"),
    (True, has_torch, has_jax),
    (NumpyInterface, has_torch and TorchInterface, has_jax and JaxInterface),
):
    if available:
        AVAILABLE[name] = Interface

# --- Get / set preferred backend ---


class backend(ArrayInterface):
    """
    Holds preferred backend state and references to available backends.

    Importing a `backend` instance is a workaround to importing
    (possibly unavailable) backends, which is useful if trying to define
    a backend-agnostic interface.
    """

    Array: typing.TypeAlias = Union[tuple(i.Array for i in AVAILABLE.values())]
    Device: typing.TypeAlias = Union[tuple(i.Device for i in AVAILABLE.values())]
    asarray: Callable = classmethod(lambda cls, x: cls.interface.asarray(x))
    interface: Any = None

    @classmethod
    def init(cls):
        cls.available = AVAILABLE
        if "QML_BACKEND" in os.environ:
            cls.use(cls.get(os.environ["QML_BACKEND"]))
        elif has_torch:
            cls.use("torch")
        elif has_jax:
            cls.use("jax")
        else:
            cls.use("np")

    def __init__(self, name: Union[str, ArrayInterface]):
        self._current = self.interface
        self._backend = self.get(name)

    def __enter__(self):
        self.__class__.interface = self._backend
        return self._backend.module

    def __exit__(self, ex_type, ex_value, ex_msg):
        self.__class__.interface = self._current
        return True

    @classmethod
    def get(cls, t: typing.Any = None) -> ArrayInterface:
        # return backend from environment
        if t is None:
            return cls.interface
        # return backend from query
        if isinstance(t, str) and t in cls.available:
            return cls.available[t]
        # return B if t : B.Array
        elif isinstance(t, cls.interface.Array):
            return cls.interface
        # retrieve interface of t
        elif isinstance(t, cls.Array):
            for backend in cls.available.values():
                if isinstance(t, backend.Array):
                    return backend
        # fall back to numpy
        return cls.available["np"]

    @classmethod
    def use(cls, backend: str):
        if isinstance(backend, ArrayInterface):
            cls.interface = backend
        elif backend in cls.available.keys():
            cls.interface = cls.available[backend]
        return cls.interface

    @classmethod
    def asarray(cls, t):
        return cls.interface.asarray(t)

    @classmethod
    def device_put(cls, t):
        return cls.interface.device_put(t)

    @classmethod
    def concat(cls, ts: Iterable, dim: int = 0):
        return cls.interface.module.concat(ts, dim)


backend.init()
