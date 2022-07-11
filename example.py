from fp.meta      import Arrow, Prod, Type
from fp.instances import List, Str, Int, Float, Bool, Wrap

from fp.meta import RingMeta

x = List(Str)(["abc", "d", "ef"])
y = List(Int)([0, 1, 2])

foo = Arrow(Str, Int)(len)
bar = Arrow(Int, Str)(lambda n: "|" * n)

foobar = foo @ bar
barfoo = bar @ foo

from fp import Tensor, Tens
import torch

# permissive tensors
x = Tensor.ones([3], dtype=torch.long)

# typed tensors
T = Tens([5])
y = T.ones()

from fp import Linear
f = Linear([5], [3])(torch.randn([3, 5]))
g = Linear([3], [5])(f.data.T)

# matrix composition
fg = f @ g
# matrix application
x = Tensor([1, 1, 0])
fg(x)

# cosheaf structure
Ta = Tens([2, 3, 6])
Tba = Ta.proj(0, 2)
Tab = Ta.embed(0, 2)
Tb = Tba.tgt

x, y = Ta.randn(), Tb.randn()
print(repr(Tba))
print('\n')
print(Tba(x))
print('\n')
print(Tab(y))
