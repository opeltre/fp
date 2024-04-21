from fp.instances import *
from fp.tensors import Tens, Tensor, Torch, Numpy, Jax


E = Tens((4, 3))

idx = E.range()
idx.shows("idx")

E.add("idx").show()

#--- switch backends

x = idx.numpy().shows("x")
y = idx.jax().shows("y")
z = idx.torch().shows("z")

class A:
    x = 0

class B(A):
    y = 1
