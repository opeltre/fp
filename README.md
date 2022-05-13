# Types in Python

The python language allows some kind of functorial and polymorphic constructs via [metaclasses](https://www.python.org/dev/peps/pep-3115/): they are synonyms of type constructors, allowing to dynamically create types and customize type construction. They provide a functionality somehow close to what [C++ templates](https://www.cplusplus.com/doc/oldtutorial/templates/) would do, although in a more convoluted way. 

The way python usually bypasses polymorphism is by providing classes as keyword arguments in the `__init__` function. For instance where C++ would force you to use a `tensor<float>` class, one would do:
```py
x = torch.tensor([0., 1., 2., 3.], dtype=torch.float)
y = torch.tensor([0., 1., 2., 3.], dtype=torch.double)
```
Types are just a prerequisite for [functorial](https://en.wikipedia.org/wiki/Functor_(functional_programming)) constructs, which have already had a vast diversity of applications in functional languages from container data types to stateful programs design, I/O operations and error handling. 
 
## Example

```py
>>> List
Functor : List
>>> type(List)
Functor : * -> *
>>> type(List(str))
Type : *

>>> Int = Id(int)
>>> x = Int("abc", base=16)
>>> x
Int : 2748
>>> xs = List(Int)([0.3, 4.3, "8"])
>>> xs
List Int : [Int : 0, Int : 4, Int : 8]
>>> List(str)("hijkl")
List str : ['h', 'i', 'j', 'k', 'l']

>>> f = Arr(str, int)(len)
>>> f
str -> int : len
>>> f("abcde")
5

>>> @Arr(str, int)
... def length(s): return len(s)
...

>>> List.fmap(f)
List str -> List int : fmap len
>>> List.fmap(["abc", "de", "f"])
List int : [3, 2, 1]
```
