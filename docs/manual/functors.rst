Functors and Monads
===================

An important motivation for typed and functional programming is support for 
so-called *type-polymorphism*: some types (e.g. lists, arrays, ...) depend on other 
types that should be treated as parameters (e.g. data type, device, ...). 

Note that python's growing support for parametricity is not very satisfactory yet: 
    
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

In `fp`, polymorphic types are explicitly created by calling a type constructor. 
The constructor's `__new__` method will be wrapped within `functools.cache`,
in order to always return the same type instance when called with identical 
(hashable) arguments.

This way, parameterized list types start behaving like we want them to:
    
    >>> List(Int) is List(Int)
    True
    >>> List(Int) == List(Str)
    False
    >>> isinstance(List(Int), List) and issubclass(List, Type)
    True

Functors 
--------
In `category theory`_, a *functor* is a transformation of categories, i.e. something 
which transforms both their *objects* (e.g. `Type` instances) and their *morphisms* 
(e.g. typed programs `A -> B` between any two `Type` instances) while preserving
source and target compositions of morphisms. 

The `List` type constructor is the canonical example of a 
`functor in functional programming`_. As an instance of the `Functor` metaclass, 
it registers the following `Method` instances: 
* `new` : `Type -> Type` image of type objects
* `fmap` : `(A -> B) -> List A -> List B` image of type morphisms
 
.. _category theory: https://wikipedia.org/wiki/category_theory
.. _functor in functional programming: https://en.wikipedia.org/wiki/Functor_(functional_programming)

Top-Type
^^^^^^^^
Functors inherit their type construction logic from the `Constructor` metaclass, 
which means they will look for a class attribute `Object` from which every *image* object 
will inherit. This special `Type` object is referred to as *top-type* throughout the documentation. 
It might be thought of as a kind of "abstract base class" (although in practice it has nothing to do 
with the `abc` module). 

As a canonical example, consider the following minimal implementation of the 
`List` functor: 

.. code-block:: python

    class List(Monoid, metaclass=Functor):

        src = Type
        tgt = Type
        
        class Object(list):

            def __init__(self, xs):
                """Cast inputs to type argument."""
                # NOTE: List(A)._head_ = List
                #       List(A)._tail_ = (A,)
                A = self._tail_[0] 
                super().__init__(fp.io.cast(x, A) for x in xs)

        @classmethod
        def fmap(cls, f):
            ...

We first see that as a functor, `List` has two class attributes `src` and `tgt`, both referring here 
to the `Type` category (these attributes are used later to determine how *morphisms* should be
mapped, see below).  
The `List.Object` class acts as a template class from which all child instances of the form 
`List(A)` inherit, and one can therefore check that `xs` is a typed list with 
`isinstance(xs, List.Object)`. 

The type arguments with which a functor or constructor was called 
can be retrieved in the tuple class attribute `_tail_`, while the constructor itself is 
stored as the class attribute `_head_`. These two attributes provide the symbolic description 
of `fp`'s typesystem which allows for convenient generic programming. 

In some cases, the functor might construct types which do more than *only* inheriting
from the top-type with a specific `_tail_` attribute. In that case, the `new` class method
should be overriden, although this requires a deeper understanding of how python metaclasses
work.

Fmap
^^^^

To complete the definition of `List` as a functor (and not only a constructor), there only 
remains to fill in the definition of the `fmap` classmethod. 

Remember from above that `List.fmap` should take a typed function `f : A -> B` as input 
and return a *mapped* function of signature `List A -> List B`. 

.. code-block:: python

    class List(Monoid, metaclass=Functor):
        ...

        @classmethod
        def fmap(cls, f):
            """
            Map a function on lists.
            """
            @Type.Hom(cls(f.src), cls(f.tgt))
            def mapf(xs):
                return (f(x) for x in xs)

            mapf.__name__ = f"map {f.__name__}"
            return mapf

The decorated `mapf` returns a generator to save the overhead of creating an intermediate list, 
while the returned typed callable `List.fmap(f)` will take care of casting its output
to `List(f.tgt)`. 


Monads
------
