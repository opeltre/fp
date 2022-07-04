# Types in Python

The python language allows some kind of functorial and polymorphic constructs via [metaclasses](https://www.python.org/dev/peps/pep-3115/): they are synonyms of type constructors, allowing to dynamically create types and customize type construction (they provide a functionality somehow close to what [C++ templates](https://www.cplusplus.com/doc/oldtutorial/templates/) would do).

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
>>> f = fp.Arrow(Str, Int)(len)
>>> f
Str -> Int  : len
>>> List.fmap(f)
List Str -> List Int : fmap len
>>> List.fmap(f)(x)
List Int    : [5, 5, 1]
```
Types are a prerequisite for [functorial](https://en.wikipedia.org/wiki/Functor_(functional_programming)) constructs, which have a vast diversity of applications in functional languages e.g. container data types, stateful programs, (a)synchronous I/O operations, log and error handling..

Type polymorphism (emulated by python metaclasses) is a powerful way to generate sister classes automatically . Just like C++ templates would allow, one can append functionality to 
existing code in a flexible and robust manner, without repeating code or creating tangled inheritance diagrams. 

## Example

Curried arrows
```py
>>> Int.add
Int -> Int  -> Int : add
>>> Int.add(2)
Int -> Int  : add 2
>>> Int.add(2, 3) == Int.add(2)(3)
True
```
Torch tensors
```py
from fp import Tensor
import torch

>>> t = Tensor.randn([3])
>>> t.data.dtype
torch.float32
>>> Tensor.mul(t)
Tensor -> Tensor : mul [1.8948, -0.6545, -0.2041]
```
