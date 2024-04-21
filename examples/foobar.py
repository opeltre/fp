from fp import *
from fp.meta import *

#### List functor ####
x = List(Str)(["abc", "defgh", "ijkl"])
y = List(Int)([0, 1, 2])

#### Hom bifunctor ####
foo = Hom(Str, Int)(len)
bar = Hom(Int, Str)(lambda n: "|" * n)

foo.shows("foo")
bar.shows("bar")

# composition 
foobar = foo @ bar
barfoo = bar @ foo

#### Functorial maps ####

x.shows("x")
List.fmap(bar @ foo)(x).shows("map (bar . foo) x")

### Either type ###

E = Either(Str, Int)
Ebar = E.fmap(bar)
Ebar.shows("Either bar")

### Product type

P = Prod(Str, Int)
p = P(Str("abcd"), Int(8))
Pf = Prod.fmap(foo, bar)
Pf.shows("Prod (foo, bar)")

p.shows("x")
Pf = Prod.fmap(foo, bar).show()
Pf(p).shows("y")

