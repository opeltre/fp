from contextlib import contextmanager

import typing
from .tensor_base import TensorBase
from .backend import Backend
from .interfaces import INTERFACES, HAS_JAX, HAS_TORCH, jax, torch
from .interfaces import StatefulInterface
from fp.base import List


class Numpy(Backend(INTERFACES["numpy"]), TensorBase):

    def is_floating_point(self):
        return self.data.is_floating_point()

    def is_complex(self):
        return self.data.is_complex()

    def norm(self, p="fro", dim=None):
        return self.data.norm(p, dim)


if HAS_JAX:

    from jax.tree_util import register_pytree_node_class

    @register_pytree_node_class
    class Jax(Backend(INTERFACES["jax"]), TensorBase):

        def tree_flatten(self):
            return ((self.data,), None)

        @classmethod
        def tree_unflatten(cls, aux_data, children):
            return cls(*children)


if HAS_TORCH:

    class Torch(Backend(INTERFACES["torch"]), TensorBase):

        @property
        def size(self):
            return self.data.numel()

        @classmethod
        def sparse(cls, shape, indices, values=None):
            ij = (
                indices
                if isinstance(indices, torch.Tensor)
                else torch.tensor(indices, dtype=torch.long)
            )
            val = (
                torch.ones([ij.shape[-1]]) if isinstance(values, type(None)) else values
            )
            t = torch.sparse_coo_tensor(ij, val, size=shape)
            return cls(t)

        def is_floating_point(self):
            return self.data.is_floating_point()

        def is_complex(self):
            return self.data.is_complex()

        def norm(self, p="fro", dim=None):
            return self.data.norm(p, dim)

        def tile(self, repeats: tuple[int, ...]):
            return self.__class__(self.data.repeat(repeats))

        # ---

        def __str__(self):
            return (
                str(self.data)
                .replace("tensor(", "")
                .replace("\n       ", "\n")
                .replace(")", "")
            )

        def __repr__(self):
            return str(self)


stateful_interface = StatefulInterface.mock()


class Tensor(Backend(stateful_interface), TensorBase):

    _Array_ = typing.Union[*(api.Array for api in INTERFACES.values())]

    @classmethod
    @contextmanager
    def use(cls, backend: str):
        """Context manager handling global backend state."""
        try:
            with StatefulInterface.use(INTERFACES[backend]):
                yield INTERFACES[backend]
        finally:
            ...

    def __repr__(self):
        return repr(self.data)

    def __str__(self):
        return "x".join(str(n) for n in self.shape)


### hack avoiding circular imports (for cast methods)
TensorBase.Numpy = Numpy
TensorBase.Jax = Jax if HAS_JAX else Numpy
TensorBase.Torch = Torch if HAS_TORCH else Numpy
###

# export available backends
backends = List(Backend)([Numpy])
if HAS_JAX:
    backends = backends + [Jax]
if HAS_TORCH:
    backends = backends + [Torch]
