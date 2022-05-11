from fp.meta      import Arrow, Prod, Type
from fp.instances import List, Str, Int, Float, Bool, Wrap

from fp.meta import RingMeta

x = List(Str)(["abc", "d", "ef"])
y = List(Int)([0, 1, 2])

foo = Arrow(Str, Int)(len)
bar = Arrow(Int, Str)(lambda n: "|" * n)

foobar = foo @ bar
barfoo = bar @ foo

from fp import Tensor
import torch

x = Tensor(torch.ones([3]))
