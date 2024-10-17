from .tensor_base import TensorBase
from .backend import Backend
from .interfaces import INTERFACES, HAS_JAX, HAS_TORCH, jax, torch
from fp.instances import List


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

        @classmethod
        def cast(cls, x):
            if isinstance(x, jax.Array):
                return cls(x)

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


class Tensor(Torch): ...


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
