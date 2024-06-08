# ---------

from fp.tensors import Tensor, Tens
import torch

# Tensor : permissive tensors
x = Tensor.ones([3], dtype=torch.long)

# Tens : typed tensors, contravariant on domains
T = Tens([5])
y = T.ones()

# Linear bifunctor
from fp import Linear

f = Linear([5], [3])(torch.randn([3, 5]))
g = Linear([3], [5])(f.data.T)

# matrix composition
fg = f @ g
# matrix application
x = Tensor([1.0, 1.0, 0.0])
fg(x)

# functoriality : cosheaf structure
Ta = Tens([2, 3, 6])
Tba = Ta.proj(0, 2)
Tab = Ta.embed(0, 2)
Tb = Tba.tgt

xa, xb = Ta.randn(), Tb.randn()
print(repr(Tba))
print("\n")
print(Tba(xa))
print("\n")
print(Tab(xb))

# Tensor products
from fp import Otimes

E = Tens([3, 2])
F = Tens([6, 4])
EF = Otimes(E, F)
