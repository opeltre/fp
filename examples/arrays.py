from fp.instances import *
from fp.meta import Type, HomFunctor
from fp.tensors import *
import fp.utils as utils


E = Tens((4, 3))
F = Tens((6,))

idx = E.range()
idx.shows("idx")

E.add(idx).show()

# --- switch backends

x = idx.numpy().shows("x")
y = idx.jax().shows("y")
z = idx.torch().shows("z")

# --- linear maps

LinEF = Linear(E, F)


# --- jax.jit compilation

import jax

add = jax.jit(lambda x, y: x + y)
add(x.jax(), y)
