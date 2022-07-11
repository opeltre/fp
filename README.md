# Types in Python

The python language allows some kind of functorial and polymorphic constructs via [metaclasses](https://www.python.org/dev/peps/pep-3115/): they are synonyms of type constructors, allowing to dynamically create types and customize type construction (providing a functionality somehow close to what [C++ templates](https://www.cplusplus.com/doc/oldtutorial/templates/) would do).

This library constructs a functional type theory inside python's runtime type system, by defining e.g. functor, monad, ... metaclasses and common class instances e.g. Float, Str, List, State, ... including a convenient 
Tensor API obtained by applying a wrapper monad to the `torch.Tensor` type.

```py
>>> import fp
>>> from fp import List, Str, Int

#-- List type constructor 
>>> type(List)
Functor : * -> *
>>> List(Str)
Type : List Str
>>> x = List(Str)(["hello", "world", "!"])

#-- List functor
>>> f = Str.len
>>> List.fmap(f)
List Str -> List Int : fmap len
>>> List.fmap(f)(x)
List Int : [5, 5, 1]
```
Types are a prerequisite for [functorial](https://en.wikipedia.org/wiki/Functor_(functional_programming)) constructs, which have a vast diversity of applications in functional languages e.g. container data types, stateful programs, (a)synchronous I/O operations, log and error handling..

Type polymorphism (emulated by python metaclasses) is a powerful way to generate sister classes automatically . Just like C++ templates would allow, one can append functionality to 
existing code in a flexible and robust manner, without repeating code or creating tangled inheritance diagrams. 

## Typed functions

Arrow types
```py
from fp import Arrow

@Arrow(Int, Str)
def bar(n):
    return '|' * n

foo = Arrow(Str, Int)(len)
```
Composition
```py
>>> foo @ bar
Int -> Int : foo . bar
>>> (bar @ foo)(12)
Str : '||||||||||||'
```

Automatic curryfication
```py
>>> Int.add
Int -> Int  -> Int : add
>>> Int.add(2, 3)
Int : 5
>>> Int.add(2)
Int -> Int : add 2
>>> List.fmap(Int.add(2))([3, 6, 9])
List Int : [5, 7, 11]
```

## Typed tensors

The (type unsafe) `torch.Tensor` class is wrapped inside the `fp.Tensor` class. This is taken care of by a custom `Wrap` monad lifting algebraic methods e.g. `+, -, *` to the wrapping class.

```py
from fp import Tensor
import torch

>>> t = Tensor.randn([3])
>>> t.data.dtype, t.data.device
(torch.float32, device(type='cpu'))

# No error raised
>>> x = Tensor.ones([4])
>>> Tensor.mul(t) @ Tensor.add(x)
Tensor -> Tensor : mul [1.8948, -0.6545, -0.2041] . add [1., 1., 1., 1.]
```
Specific tensor types are obtained by the `Tens` functor, which is contravariant on domain shapes:

```py
from fp import Tens

>>> T = Tens([3])
>>> T.ones()
Tens 3 : [1., 1., 1.]
```
Linear maps acting by `n x m` matrices subclass both `Tens([n, m])` and `Arrow(Tens([m]), Tens([n]))`:

```py
>>> from fp import Linear

>>> f = Linear([3], [4]).randn()
>>> f
Linear 3 -> 4 : mat 4x3
>>> f(x)
Tens 4 : [-5.5333,  2.7625,  3.0484, -1.0863]
```


