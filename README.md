# fp

A lightweight functional programming library with 
[numpy], [jax] and [torch] support. 

- 🗒️ [docs]
- 📁 [repository]

[docs]:https://https://funprogram.readthedocs.io/en/latest/
[repository]:https://github.com/opeltre/fp
[numpy]:https://numpy.org
[jax]:https://jax.readthedocs.io/en/latest/
[torch]:https://pytorch.org/docs

## Installation 

There are two ways that you can start using `fp`. 
This library is still under development, 
but beta versions will updated as necessary on PyPI.

### poetry environment

```bash
git clone https://github.com/opeltre/fp
cd fp && poetry install
```

### pip install

```
pip install funprogram
```

## Overview

The `fp` library relies on python [metaclasses] to emulate a static python type system of `Type` instances. 

Its motivation is to provide a strict yet flexible interface 
to a polymorphic type system, implementing most the 
abstractions of a [cartesian closed] category. 
Being familiar with category theory is not a prerequisite for using `fp`. 
The package and documentation are also intended as a user-friendy 
and didactic tools for getting used with functional programming concepts. 

[cartesian closed]: https://en.wikipedia.org/wiki/Cartesian_closed_category

[metaclasses]: https://www.python.org/dev/peps/pep-3115/ 

Type polymorphism was a necessary feature for the 
downstream message-passing library [topos] that I started developing 
during my PhD. 
Overcoming the mysterious difficulties of metaclass construction was a hard enough task for this latter project to ever really reach a definitive state, but development might perhaps resume as stable versions of the `fp` package are released. 

[topos]: https://github.com/opeltre/topos 

### `fp.cartesian` module

The type `Hom(A, B)` declares typed functions or type _morphisms_, with input in `A` and output in `B`. Functions with multiple inputs can be declared by supplying a tuple of types `A = (A0, A1, ...)` as input.

```py
from fp import *

@Hom((Int, Str), Str)
def foo(n, s):
    return ("-" * n).join([s] * n)
```

In `fp`, typed functions are instances of the "top" type `Hom.Object` which takes care automatic currying, i.e. returning the partial application of 
the decorated callable when invoked with too few arguments. 

```py
>>> foo
Int -> Str -> Str: foo
>>> foo(2)
Str -> Str: foo 2
>>> foo(2)("Hello World!")
Str: "Hello World!--Hello World! "
```

Typed functions (including curried ones) can be composed with the `@` operator:

```py
>>> bar = Hom(Int, Str)(lambda n: '|' * n)
>>> baz = Int.mul
>>> foo(4) @ bar @ baz 
Int -> Str: foo 4 . λ . mul 3
>>> (foo(4) @ bar @ baz(3))(2)
Str: "||||||----||||||----||||||----||||||"
```

### `fp.instances` module

Algebraic subclasses  of `Type` are defined in `fp.instances.algebra`, 
allowing transparent subclassing of numeric builtin types. The lifting and propagation of algebraic methods defined there is also used by `Str` 
and `List.Object`, by being declared instances of the `Monoid` type class.

```py
>>> from fp import Int, Float, Str, List
>>> greet = Str.add("👋 Welcome")
>>> greet 
Str -> Str: add 👋 Welcome
>>> greet("! " + foo(2)(bar(3)))
"👋 Welcome! |||--|||"
```

The `List` functor creates types inheriting from `List.Objecŧ`, a subclass of list with a `map` method. The `map` method of any functorial type, e.g.
`List(Str)`, is actually an alias for the `List.fmap` class method. Only the target needs to be explicited when called with an untyped function.

```py
>>> phone = List(Int)("0632501202")
>>> phone.map(lambda n: 2 << n, tgt=Int)
List Int : [1, 64, 8, 4, 32, 1, 2, 4, 1, 4]
>>> List.fmap(bar)
List Int -> List Str: map λ
>>> List.fmap(bar)(phone)
List Str : ['', '||||||', '|||', '||', '|||||', '', '|', '||', '', '||']
```

Other features include a `State` monad with which one might indeed write 
fun programs 💻🐒!

```py
# `State(Int, Str)` subclasses `Int -> (Int, Str)`

@State(Int, Str)
def barbaz(n):
    """Update an integer and return a string."""
    q, r = divmod(n, 2)
    if q == 0:
        return q, "|" if r else "*"
    return q, "|<" if r else "*<"

# The `State(Int)` monad binds `a -> State(Int, b)` functions

@Hom(Str, State(Int, Str))
def foobarbaz(acc):
    """Do `barbaz` while the accumulator says to continue."""
    # run with io.VERBOSITY = 1 to see intermediate steps
    io.log(acc, v=1)
    if len(acc) and acc[-1] == "<":
        # accumulate output
        accbarbaz = barbaz.map(Str.add(acc[:-1]))
        # bind foobarbaz
        return accbarbaz >> foobarbaz
    else: 
        # return accumulator
        return State(Int).unit(acc)

>>> foobarbaz.run(257)
(Int, Str): (0, '|*******|')
>>> foobarbaz(260)
Str: '**|*****|'
```
Other monads have found plenty of applications 
in abstracting IO contexts, error handling, data streams and asynchronous 
threads.

See the [docs] or the [source][instances] for an exhaustive list of 
the currently implemented types, functors, monads, etc. 

[instances]: https://github.com/opeltre/fp/blob/master/fp/instances/__init__.py

### `fp.tensors` module

For now, the `Tensor` class is an alias of `Torch`, while Arrays from other backends can be explictly created with `Jax` and `Numpy`. This part of the API is
subject to change. 

```py
>>> from fp.tensors import Torch, Jax, Numpy
>>> from fp.tensors import backends
>>> backends
List Backend: [Numpy, Jax, Torch]
>>> x, y, z = (B.range(3) * (10 ** i) for i, B in enumerate(backends))
>>> x
Numpy: [0 1 2]
>>> y + x.jax() 
Jax: [0 11  22]
>>> z + (x + y.numpy()).torch()
Torch: [0, 111, 222]
```

Typed tensors are created by supplying shape tuples to the  `Tens` functor. 
With `Linear` and `Otimes`, typed tensors form a [closed monoidal] 
subcategory of `Type`.

[closed monoidal]: https://en.wikipedia.org/wiki/Closed_monoidal_category

```py
>>> from fp.tensors import Tens, Linear
>>> E = Tens((2, 3))
>>> F = Tens((4,))
>>> v = E.range()
Tens 2x3 : [[0, 1, 2],
           [[3, 4, 5]]
>>> f = Linear(E, F)(Tensor.randn(4, 6))
>>> f(v).shape
(4,)
```

See [examples/arrays.py](examples.arrays.py) and the [docs] for more details.

## Contributing and troubleshooting

If you use `fp` and experience bugs or inconsistencies, 
please report an issue on the 
[github](htts://github.com/opeltre/fp/issues) page.
When debugging `fp` code, setting the following should be useful:

```py
fp.io.VERBOSITY = 3
```