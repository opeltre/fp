# Types in Python

The python language allows some kind of functorial and polymorphic constructs via [metaclasses](https://www.python.org/dev/peps/pep-3115/): they are synonyms of type constructors, allowing to dynamically create types and customize type construction. They provide a functionality somehow close to what [C++ templates](https://www.cplusplus.com/doc/oldtutorial/templates/) would do, although in a more convoluted way. 

The more traditional, pythonic way to approach polymorphism is by providing classes as keyword arguments in the `__init__` function, as in: 
```py
x = torch.tensor([0., 1., 2., 3.], dtype=torch.float)
y = torch.tensor([0., 1., 2., 3.], dtype=torch.double)
```
However python's typesystem is completely unable to reason about the polymorphic argument with this kind of approach:
```py
type(x) == type(y)
```
Types lead to much more than code decoration, as the [typing](https://docs.python.org/3/library/typing.html) module lets you do.
Type polymorphism is a powerful way to generate sister classes automatically without repeating yourself or creating tangled inheritance diagrams (again, think of how great C++ templates are), or append functionality to your code in a flexible and robust manner. 

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
