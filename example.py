from fp import *
from fp.meta import *

import inspect

# List functor 
x = List(Str)(["abc", "d", "ef"])
y = List(Int)([0, 1, 2])

# Arrow bifunctor
foo = Arrow(Str, Int)(len)
bar = Arrow(Int, Str)(lambda n: "|" * n)

# composition 
foobar = foo @ bar
barfoo = bar @ foo

# Enumerate type class methods
for k, vk in List.methods().items():
    print(k, ':\t', vk)
