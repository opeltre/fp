from fp import *
from fp.cartesian.prod import Writer

W = Writer(Str)

x = W(Int)("abc", 3).show()
Wf = W.fmap(Int.mul(2)).show()
y = Wf(x).show()
