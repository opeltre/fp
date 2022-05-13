# Types in Python

The python language allows some kind of functorial and polymorphic constructs via [metaclasses](https://www.python.org/dev/peps/pep-3115/): they are synonyms of type constructors, allowing to dynamically create types and customize type construction. They provide a functionality somehow close to what [C++ templates](https://www.cplusplus.com/doc/oldtutorial/templates/) would do, although in a more convoluted way. 

The way python usually bypasses polymorphism is by providing classes as keyword arguments in the `__init__` function. For instance where C++ would force you to use a `tensor<float>` class, one would do:
```py
x = torch.tensor([0., 1., 2., 3.], dtype=torch.float)
y = torch.tensor([0., 1., 2., 3.], dtype=torch.double)
```
Types are just a prerequisite for [functorial](https://en.wikipedia.org/wiki/Functor_(functional_programming)) constructs, which have already had a vast diversity of applications in functional languages from container data types to stateful programs design, I/O operations and error handling. 

## Installation

```sh
git clone https://github.com/opeltre/fp && cd fp && pip install .
```

## Examples

Arrow types:
```
>>> foo = Arrow(Str, Int)(len)
>>> f
Str -> Int : len
>>> f("abcde")
Int : 5

>>> @Arrow(Int, Str)
... def bar(x): return '|' * x

>>> foo @ bar
Int -> Int : foo . bar

>>> (bar @ foo)(12)
Str : '||||||||||||'
```

List functor: 

```py
>>> List
Functor : List
>>> type(List)
Functor : * -> *
>>> type(List(Str))
Type : *
```py 
>>> List.fmap(f)
List Str -> List Int : fmap len
>>> List.fmap(["abc", "de", "f"])
List Int : [3, 2, 1]
``` 

Wrapped tensors 
```py
>>> from fp Tensor
>>> import torch
>>> x = Tensor(torch.randn([3]))
>>> x
Tensor 	:: [-0.1220, -0.5919, -0.9754]
>>> Int.add(x)
Tensor -> Tensor :: add [-0.1220, -0.5919, -0.9754]
```
