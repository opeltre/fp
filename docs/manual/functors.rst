Functors for Polymorphism
=========================

An important motivation for typed and functional programming is support for 
so-called *type-polymorphism*: some types (e.g. lists, arrays, ...) depend on other 
types that should be treated as parameters (e.g. data type, device, shape...). 

Type Polymorphism
-----------------
It is a very common problem in programming to design data structures and interfaces 
whose low-level behaviour may depend on the specific types of the objects being handled, 
although all the implementations share a common logic.  
A *single source code definition* which adapts behaviour to a range of input types 
(*type parameters* in the source) is called *polymorphic*.

Polymorphism is a powerful feature of C++, accessible via its so-called *templates*. 
This is for instance very handy if trying to implement a linear algebra backend supporting 
different numerical types and floating point precisions. 

Python came rather late to type polymorphism, with a support mostly limited to type annotations 
and not so satisfying yet: 
    
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
A constructor's `__new__` method is wrapped within `functools.cache`,
in order to always return the same type instance when called with identical 
(hashable) arguments.

This way, parameterized list types start behaving like we want them to:
    
    >>> List(Int) is List(Int)
    True
    >>> List(Int) == List(Str)
    False
    >>> isinstance(List(Int), List) and issubclass(List, Type)
    True

Covariant Functors 
------------------
   In `category theory`_, *functors* are transformations of categories, i.e. things 
   that transforms both their *objects* (e.g. `Type` instances) and their *morphisms* 
   (e.g. typed programs `A -> B` between any two `Type` instances). 
   These transformations must map any source-composition of morphisms 
   to the target-composition of image morphisms. 

The `List` type constructor is the canonical example of a 
`functor in functional programming`_. As an instance of the `Functor` metaclass, 
it implements the following `Method` instances: 

* `new` : `Type -> Type` image of type objects
* `fmap` : `(A -> B) -> List A -> List B` image of type morphisms
 
.. _category theory: https://wikipedia.org/wiki/category_theory
.. _functor in functional programming: https://en.wikipedia.org/wiki/Functor_(functional_programming)

Image objects
^^^^^^^^^^^^^
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

Image morphisms
^^^^^^^^^^^^^^^

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

Examples
^^^^^^^^

.. _tree:

.. container:: example

    .. rubric:: Trees

    As a popular simple example, consider the `Tree` functor which maps: 

    * any type `a` to the (recursive) type `Tree a = Branch a [Tree a]`. This Haskell notation instructs 
      that trees are defined by a root node carrying a value `x: a` and a list of subtrees of same 
      node type.
    * any function `f : a -> b` to the tree transformation `Tree.fmap(f) : Tree(a) -> Tree(b)` 
      recursively defined by
        
    .. code-block:: python

          Tree.fmap(f) = 
              lambda Tree.branch(x, subtrees) :
                  Tree.branch(f(x), [Tree.fmap(f)(t) for t in subtrees])

In the above pseudo-python code, a classmethod `Tree.branch` is assumed to take care 
of type inference to construct an object of type `Tree(type(x))`: remember that as a 
functor, `Tree` itself must accept type arguments, in order to return tree types such 
as `Tree(Int)` or `Tree(Tensor)`.

By imitating the `List` functor implementation outlined above, i.e.

* declaring `fp.Functor` as metaclass,
* defining an `Object` top-type as class attribute,
* implementing the `fmap` class method, 

functors will automatically cache their `__new__` type constructor, so that 

    >>> List(A) is List(A)
    True

always. More advanced type construction methods will be covered in the chapter on 
the `Constructor` metaclass, from which `Functor`, `Applicative` and `Monad` inherit 
their type construction logic.

.. _hom-functor:

.. container:: example

    .. rubric:: Covariant Hom Functors

    Given any category C and an object X of C, the *covariant hom-functor* `Hom(X, ...)` below X
    maps C into the category of sets (types), by:

    * mapping any object A of C to the set (type) `Hom(X, A)`
    * mapping any morphism (function) f : A → B to a function::

        Hom.fmap(f) : Hom(X, A) → Hom(X, B)
                      ϕ ↦  f ∘ ϕ

    called *push-forward* by f, which simply means appending f at the end of a pipe from
    a programmer's view. 


Contravariant Functors
----------------------
An important class of functors actually swap the source and target objects when transforming
morphisms. These functors are called *contravariant*, but they are really otherwise just ordinary
functors, as the direction of arrows is important yet arbitrary 
(what we choose to call source and target can be globally interchanged). 
This fundamental symmetry from say, left to right, is called *duality*. 
Dual notions are usually named with the "co-" prefix (e.g. vector, covector).

Opposite Category
^^^^^^^^^^^^^^^^^
    Given a category C, its dual or *opposite* category C*  

    * has the same objects as C,
    * has a morphism `f* : B -> A` for every morphism `f : A -> B` of C
    * has composition `f* @ g* : C -> A` equal to `(g @ f)* : C -> A` for every
      pair of composable morphisms `f : A -> B` and `g : B -> C` of C.

This defines C* as a category *for any category C*, although its (sometimes abstract)
swapped morphisms may not always be thought of as functions on sets
(that can be evaluated with `__call__`), as is the case for the many 
common `concrete categories`_ (groups, vector spaces, algebras, manifolds, posets...) 
that can be embedded in `Set`.

.. _concrete categories: https://wikipedia.org/wiki/conrete_category

In the case of vector spaces, duality still 
carries a concrete interpretation. 
Given a linear map `f : fp.Linear(A, B)` its dual is the adjoint or 
*transposed* map, `f.t() : fp.Linear(B, A)` in finite dimension 
(for topological vector spaces, the dual space A' of 
continuous linear forms on A may be quite different from A). 

Contravariance
^^^^^^^^^^^^^^
    A contravariant functor F from C to C' is a
    covariant functor from C* to C'. 

In `fp`, contravariant functors are instances of the `Cofunctor` 
metaclass. They must implement a class method `cofmap` with signature:

* `F.cofmap : Hom(A, B) -> Hom(F(B), F(A))`

There are many examples of contravariant functors in `fp`. They mostly
arise from bivariate functors, described in more details below. 

Examples
^^^^^^^^

.. _real-functions:

.. container:: example
    
   .. rubric:: Real Functions

   Ubiquitous contravariant functors link geometry and algebra in mathematics, 
   which: 
     
   * associate to any base space X (finite set or topological space,
     differentiable or algebraic manifold...)
     an algebra of real-valued functions C(X), satisfying some regularity condition 
     (continuous, continuously differentiable, polynomial or rational...)

   * map any morphism ϕ : X → Y to the *pull-back* ϕ* : C(Y) → C(X)::

       ϕ* : C(Y) → C(X) 
            f ↦  f ∘ ϕ

The restriction of real functions to a subspace X ⊂ Y is a particular case of pull-back. 
Their invariant extension along a regular projection or quotient map
π : Z → Y are another particular case of pull-back. 

These abstract but general notions have very practical counterparts when 
viewing numerical array types as a special case of cofunctors of real 
functions above.  

.. container:: example

    .. rubric:: Tensors 
    
    As a particular case, assume that X is a finite set, with an additional 
    torus structure::
    
        X = (Z/n₀Z) × … × (Z/nₖ₋₁Z)
         ~= fp.Torus((n₀, …, nₖ₋₁))

    Then C(X) = **R** :sup:`X` denotes the space of real values functions on X. 
    This space is described by the type `fp.Tens((n₀, …, nₖ₋₁))`. 

    The contravariant functor `Tens` is the object of the next chapter.
    
Contravariant functors of real functions are usually a particular case 
of the following more general example, where the line (and algebra)
of real numbers **R** plays the role of 
a particular object in the category. 

.. _hom-cofunctors: 

.. container:: example
    
    .. rubric:: Contravariant Hom Functors

    Given any category C and an object Y of C, the *contravariant hom-functor* 
    `Hom(..., Y)` above Y
    maps C into the category of sets (types), by:

    * mapping any object B of C to the set (type) `Hom(B, Y)`
    * mapping any morphism (function) f : A → B to a function::

        Hom.cofmap(f) : Hom(B, Y) → Hom(A, Y)
                        ψ ↦  ψ ∘ f

    called *pull-back* by f. From a programmer's view, it just prepends 
    f at the entrance of a pipe.


Multivariate Functors
---------------------
From a very abstract perspective, many computer data structures 
could also be thought of as special Hom bifunctors: 

* Dictionaries map finite sets of keys to a value type,
* Tensors map index ranges (hypercubes) to a numerical value type

