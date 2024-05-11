Functors and Monads
===================

An important motivation for typed and functional programming is support for 
so-called *type-polymorphism*: some types (e.g. lists, arrays, ...) depend on other 
types that should be treated as parameters (e.g. data type, device, ...). 

In `fp`, polymorphic types are explicitly created by calling a type constructor:

    >>> List(Int) is List(Int)
    True
    >>> List(Int) == List(Str)
    False
    >>> isinstance(List(Int), List) and issubclass(List, Type)
    True
    
This behaviour is obtained by wrapping the constructor's `__new__` method within `functools.cache`,
in order to always return the same type when calling the type constructor with identical arguments. 
Note the difference with python's parametric types:
    
    >>> list[int] is list[int]
    False
    >>> issubclass(list[int], list) or isinstance(list[int], list)
    False
    >>> x = list[int](x for x in (0, 1, 2, "nan", 3.141592))
    >>> isinstance(x, list[int])
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    TypeError: isinstance() argument 2 cannot be a parameterized generic
    >>> x
    [0, 1, 'nan', 3.141592]

Functors 
--------

TODO
