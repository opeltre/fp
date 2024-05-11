# fp

A lightweight functional programming library with 
[numpy], [jax] and [torch] support. 

- 🗒️ [docs]
- 📁 [repository]

[docs]:https://readthedocs.io/funprogram
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

[metaclasses]: https://www.python.org/dev/peps/pep-3115/ 

### `fp.cartesian` module

The type `Hom(A, B)` declares typed functions or type _morphisms_, with input in `A` and output in `B`. Functions with multiple inputs can be declared by supplying a tuple of types `A = (A0, A1, ...)` as input.

```py
from fp import *

@Hom((Int, Str), Str)
def foo(n, s):
    return ("-" * n).join([s] * n)
```

In `fp`, typed functions are instances of the "top" type `Hom.Object` which takes care automatic currying returning the partial application of 
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
allowing transparent subclassing of numeric builtin types. The lifting and propagation of algebraic methods is also used by `Str` 
and `List.Object`, by being instances of the `Monoid` type class.

```py
>>> from fp import Int, Float, Str, List
>>> greet = Str.add("👋 Welcome")
>>> greet("! " + foo(2)(bar(2)))
"👋 Welcome! ||--||"
```
The `List` functor creates types inheriting from `List.Objecŧ`, a subclass of list with a `map` method. The `map` method of any functorial type, e.g.
`List(Str)`, is actually an alias for the `List.fmap` class method. Only the target needs to be explicited when called with an untyped function.

```py
>>> phone = List(Int)("0632301202")
>>> phone.map(lambda n: 2 << n, tgt=Int)
List Int : [2, 128, 16, 8, 16, 2, 4, 8, 2, 8]
>>> List.fmap(bar)
List Int -> List Str: map λ
>>> List.fmap(bar)(phone)
```

See the [docs] for more.

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
With `Linear` and `Otimes`, typed tensors form a cartesian closed subcategory
of types. 

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