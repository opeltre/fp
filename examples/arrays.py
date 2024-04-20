from fp.instances import *
from fp.tensors import Tens, Tensor, Numpy, Jax


E = Tens((3, 2))

idx = E.range()
idx.shows("idx")

E.add("idx").show()


x = Numpy.zeros((2, 6)).shows("x")
y = Jax.zeros((3, 4)).shows("y")
z = Tensor.zeros((4, 3)).shows("z")

