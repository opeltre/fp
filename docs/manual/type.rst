The `Type` Category
===================

Although deep knowledge of category theory is 
not required to use `fp` library, understanding its basic vocabulary and concepts 
should be very valuable. 
We also hope that this Python library will encourage
unfamiliar users to learn how functional languages 
represent polymorphic types and programs, 
stateful or asynchronous computations, 
I/O and error-handling... without 
the hustles of moving to a foreign language and losing the rich Python ecosystem.

Introduction
------------

This manual will sequentially introduce all the relevant concepts that are embodied by 
some (meta)class in the `fp` library. Let us also mention that the
Wikipedia is also a very valuable resource 
on both the mathematical and programming aspects of `category theory <categories>`_. 

Let us start with our very first mathematical definition, 
     
    Category: 
        A category **C** is defined by

        * a class of *objects* denoted :math:`{\rm Obj}({\bf C})`
          (e.g. the class of sets, vector spaces, types...)
        * a set of arrows or *morphisms* :math:`{\rm Hom}_{\bf C}(A, B)` 
          (e.g. functions, linear maps, typed programs...) whose
          elements are denoted by :math:`f : A \to B`, for every objects :math:`A, B`, 
        * a *composed morphism* :math:`g \circ f : A \to C`
          for every pair of composable morphisms :math:`f : A \to  B` 
          and :math:`g : B \to C`
        * an *identity morphism* :math:`1_A : A \to A` for
          every object :math:`A`, which fixes any composable morphism by left and right compositions 
          respectively.

        The composition is furthermore demanded to satisfy 
        :math:`h \circ (g \circ f) = (h \circ g) \circ f` 
        for every triplet of composable morphisms, composition 
        is said to be *associative*.

`Categories`_ and `functors`_ were introduced in the 1950s 
by mathematicians Eilenberg and Steenrod to classify topological spaces by their homology groups.
Somehow surprisingly, category theory has also found profound applications in computer science and 
logic since (see for instance the `Curry-Howard`_ correspondence).

.. _Categories: https://wikipedia.org/category_(mathematics)
.. _functors: https://en.wikipedia.org/wiki/Functor_(functional_programming)
.. _Curry-Howard: https://en.wikipedia.org/wiki/Curry%E2%80%93Howard_correspondence


Example
^^^^^^^
.. container:: example

    .. rubric:: Types

    The `Type` category is described by: 
    
    * the class of objects :math:`{\rm Obj}({\tt Type})` described by 
      `isinstance(..., Type)`,
    * type of programs (functions) `Hom(A, B)` for any pair of input/output types 
      `A` and `B`, 
    * a composed program `g @ f` for every composable pair `f : Hom(A, B)` 
      and `g : Hom(B, C)`,
    * an identity function `Hom.id(A) : Hom(A, A)` for every type `A`.

    Note that within the library, `fp.Hom` is an alias to `fp.Type.Hom`.



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

    >>> n = Int("fp", base=32)
    Int : 505
    >>> isinstance(n, int)
    True
    >>> [isinstance(T, Type), for T in (Int, int)]
    [True, False]

Instances of `Type` are referred to as type *objects*, as `Type` forms 
a `cartesian closed category`_.

.. _cartesian closed category: https://en.wikipedia.org/wiki/Cartesian_closed_category

Type Morphisms 
--------------

A type *morphism* `f: A -> B` refers to a pure, typed function with input in `A` and 
output in `B`. 

Because morphisms is a shorthand for *homomorphism* in mathematical 
terminology, the type of pure functions from `A` to `B` is generically 
denoted by `Hom(A, B)`. This type accepts any plain python callable, which means 
it may be used as a function decorator: 
    
    >>> @Hom(Int, Str)
    ... def bar(n):
    ...     return n * "|"
    >>> bar
    Int -> Str : bar

The `axioms of a category <https://wikipedia.org/category_(mathematics)>`_ 
demand that morphisms are equipped with the following structure: 

* For every type `A`, there is an identity morphism: `Hom.id(A)` of type `A -> A`.
* For any morphisms `f: A -> B` and `g : B -> C`, there 
  is a composed morphism `g @ f : A -> C`. 

It is also required that (i) left/right composition with the identity is the 
identity and (ii) composition is *associative*, i.e. `h @ (g @ f) == h @ (g @ f)`
for every composable triple `f, g, h`.

**Note:** The fact that `Hom(A, B)` is itself an instance of `Type` is an additional 
axiom of *cartesian categories*. The categories of sets and vector spaces are also 
cartesian (i.e. they have sets of functions and vector spaces of linear maps as objects). 
In many other interesting examples, the set of morphisms `Hom(A, B)` is only required 
to be a set, but not an object of the category (e.g. in a partial order such as `Keys`, 
the set of arrows `A -> B` is a point when `A` is contained in `B` and empty otherwise).

.. _cartesian categories: https://en.wikipedia.org/wiki/Cartesian_monoidal_category

    >>> foo = Hom(Str, Int)(len)
    >>> foo
    Str -> Int : len
    >>> foo @ bar 
    Int -> Int : len . bar
    >>> bar @ foo
    Str -> Str : bar . len
    >>> isinstance(type(bar), Type) and type(bar) is Hom(Int, Str)
    True

Typed functions of `Hom(A, B)` store their computation sequence in a tuple:
an empty tuple is an identity, and concatenated tuples describe compositions.
This yields a truely associative representation of function pipes, avoids the stack growth 
of nested function closures, and enables composing an arbitrary 
number of functions at the small cost of tuple instance creation. 

    >>> baz = Hom(Str, Int)(lambda s: s.count("*"))
    ...
    # Typed compositions compare their internal tuple
    >>> foo @ (bar @ baz) == (foo @ bar) @ baz
    True
    >>> foo @ bar @ baz == Hom.compose(baz, bar, foo)
    True
    >>> foo @ bar @ baz
    Str -> Int : len . bar . λ
    ...
    # Input redirection `<<` will execute last
    >>> foo @ bar @ baz << "M*ule * G*uffres!"
    (Int: 3)

Type checks and type casts only happen at the entrance and exit of the pipe. 
Future versions of the library might include switches to customize this 
behaviour, e.g. warn on implicit type casts as the python `isinstance` builtin 
might incur a little overhead. 

Type Sums and Products
----------------------

A fascinating aspect of category theory is its ability to succinctly describe 
almost all mathematical concepts with simple arrow diagrams. 
In particular, sums ans products are characterized by their so-called 
`universal properties`_. This means that defining sums or products is not at all 
arbitrary, but enforced by the categorical structure (objects, arrows and identities), 
whenever sums and/or products exist. 
The `Type` category (just like sets and vector spaces) has both sums and products, 
obtained by the `Either` and `Prod` type constructors. 


.. _universal properties: https://wikipedia.org/wiki/universal_property

In `fp`, the universal property of sums is called `gather`:
::

    Either.gather: ((A -> Y), (B -> Y),  ...) -> Either(A, B, ...) -> Y

and the dual universal property of products is called `branch`:
::

    Prod.branch: ((X -> A), (X -> B), ...) -> X -> Prod(A, B, ...)


