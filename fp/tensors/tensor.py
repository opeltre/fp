from .backend import Backend, NumpyAPI, TorchAPI, JaxAPI, has_jax, has_torch, has_jax, has_torch
from .tensor_base import TensorBase
from fp.instances import List


class Numpy(Backend(NumpyAPI()), TensorBase):

    def is_floating_point(self):
        return self.data.is_floating_point()

    def is_complex(self):
        return self.data.is_complex()

    def norm(self, p="fro", dim=None):
        return self.data.norm(p, dim)

class Jax(Backend(JaxAPI()), TensorBase):
    ...

class Torch(Backend(TorchAPI()), TensorBase):
    
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
        val = torch.ones([ij.shape[-1]]) if isinstance(values, type(None)) else values
        t = torch.sparse_coo_tensor(ij, val, size=shape)
        return cls(t)

    def is_floating_point(self):
        return self.data.is_floating_point()

    def is_complex(self):
        return self.data.is_complex()

    def norm(self, p="fro", dim=None):
        return self.data.norm(p, dim)

    def tile(self, repeats: tuple[int,...]):
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

class Tensor(Torch):
    ...

### hack avoiding circular imports (for cast methods)
TensorBase.Numpy = Numpy
TensorBase.Jax = Jax
TensorBase.Torch = Torch
###

# export available backends
backends = List(Backend)([Numpy])
if has_jax: 
    backends = backends + [Jax]
if has_torch: 
    backends = backends + [Torch]

