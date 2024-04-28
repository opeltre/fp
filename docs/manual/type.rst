The `Type` Category
===================

Although deep knowledge of category theory is 
not required to use fp, 
one should know that the Wikipedia is a very qualitative and valuable resource
on both the mathematical and programming aspects of category theory, 
users are encouraged to search there for additional context and information.

The attributes defining a category are:
    * a class of *objects* (e.g. the class of sets, vector spaces, types, ...)
    * a class of *arrows* or *morphisms* (e.g. functions, linear maps, typed programs, ...)

`Categories`_ and `functors`_ were introduced in the 1950s 
by mathematicians Eilenberg and Steenrod to classify topological spaces by their homology groups.
Somehow surprisingly, category theory has also found profound applications in computer science and 
logic since (see for instance the `Curry-Howard`_ correspondence). 


.. _Categories: https://wikipedia.org/category_(mathematics)
.. _functors: https://en.wikipedia.org/wiki/Functor_(functional_programming)
.. _Curry-Howard: https://en.wikipedia.org/wiki/Curry%E2%80%93Howard_correspondence

Type Objects
------------

All types within fp are instances of the metaclass `fp.meta.type.Type`, 
which for instance takes care of pretty-printing type annotations of 
typed values.

    >>> from fp import *
    >>> isinstance(Int, Type)
    True
    >>> Int(8)
    Int : 8

The `Int` class is a subclass of the python builtin `int`. Its behaviour is 
only decorated by the metaclass `type(Int) == Ring`, a subclass of `Type`.

    >>> fp = Int("fp", base=32)
    Int : 505
    >>> isinstance(fp, int)
    True
    >>> [isinstance(T, Type), for T in (Int, int)]
    [True, False]

Instances of `Type` are referred to as type *objects*, as `Type` forms 
a `cartesian closed category`_.

.. _cartesian closed category: https://en.wikipedia.org/wiki/Cartesian_closed_category

An important motivation for typed and functional programming is support for 
so-called *type-polymorphism*: some types (e.g. lists, arrays, ...) depend on other 
types that should be treated as parameters (e.g. data type, device, ...). 

In `fp`, polymorphic types are explicitly created by calling a cached metaclass-defined constructor.

    >>> List(Int) is List(Int)
    True
    >>> List(Int) == List(Str)
    False
    >>> isinstance(List(Int), List) and issubclass(List, Type)
    True
    
This behaviour is obtained by wrapping the constructor's `__new__` method within `functools.cache`,
in order to always return the same type when calling a type constructor with the same arguments. 

Note that calling a type constructor behaves quite differently from python's parametric types:
    
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



Type Morphisms 
--------------

A type *morphism* `f: A -> B` refers to a pure, typed function with input in `A` and 
output in `B`. 

