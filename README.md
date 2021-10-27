# Emulating Types in Python

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
