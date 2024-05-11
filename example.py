import fp
from fp.meta      import Arrow, Prod, Type
from fp.instances import List, Str, Int, Float, Bool, Wrap

# List functor 
x = List(Str)(["abc", "d", "ef"])
y = List(Int)([0, 1, 2])

# Arrow bifunctor
foo = Arrow(Str, Int)(len)
bar = Arrow(Int, Str)(lambda n: "|" * n)

# composition 
foobar = foo @ bar
barfoo = bar @ foo

