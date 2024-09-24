Natural Transformations
-----------------------
A fascinating aspect of category theory is its multiscale description of modern mathematics 
both at structure level and theory level. For instance, 

* a `group`_ is a category (with only one object • and a set of invertible morphisms 
  g : • → •) while all groups form the objects of the **Grp** category 
  (with group morphisms as morphisms) 
* a `partial order`_ is a category (with arrows from lower to greater elements) 
  while all partial orders form the objects of the **Ord**
  category (with increasing functions as morphisms)

In both examples above, one might check that morphisms actually coincide with **functors** 
from one structure (group/partial order) to an other structure (each a category).

Naturality 
^^^^^^^^^^
`Natural transformations`_ are a cornerstone of category theory. As functors describe relationships 
between categories, natural transformations describe 
relationships beween functors.

.. _natural transformations: https://en.wikipedia.org/wiki/Natural_transformation 

Given two functors F and  G from C to C', 
a natural transformation T : F → G is defined by 
a collection `T[a] : F(a) -> G(a)` such that for all 
`ϕ : a -> b`, one has: 
::

    G.fmap(ϕ) @ T[a] = T[b] @ F.fmap(ϕ)

To characterize natural transformations, one thus usually says that the following 
diagram *commutes*:
::

                       T[a]
                 F(a) -----> G(a) 
                  |           |
                ϕ |           | ϕ
                  v           V
                 F(b) -----> G(b)
                       T[b]


Functor Categories
^^^^^^^^^^^^^^^^^^
With the above definitions, 
one may define a *category of functors* from C to C' and usually denoted [C, C'] 
(or `C' ** C` in exponent format) given two categories C and C'. 
Its objects are functors from C to C', and morphisms are natural transformations 
between such functors. 

If follows that functors from `Type` to `Type` form a special category, called 
the category of type *endofunctors*.

Examples
^^^^^^^^
A *group representation* is a functor ρ : G → **Vect** mapping the group's unique object • to 
a vector space V, and mapping every group element g : • → • to a linear 
isomorphism ρ(g) : V → V. 
A morphism of representations T : ρ → ρ'  is a *natural transformation* from ρ to ρ'.


Natural transformations play an important role in functional programming, as 
we shall see further in the manual. 
As a first example, consider the `Tree` functor defined above.
Then there is a natural transformation `flatten: Tree -> List` such that for every 
type `a`,

* `flatten[a]` maps `Tree(a)(x, [])` to `[x]` (leaves)
* `flatten[a]` maps `Tree(a)(x, subtrees)` to `[x, *flatten[a](t) for t in subtrees]` (recursion)

The fact that actual implementations do not depend on the type parameter `a` 
(only type signatures do) is a sign of naturality. 

In many other examples, explicit knowledge 
of natural maps `T[a] : F(G(a)) -> G(F(a))` (commutation relation) between two functors 
is very useful. 
Assume for instance that `F = List` and `G = Async` (mapping type `a` to a promise 
for a value `x: a`). Then a natural transformation 

* `parallel : List @ Async -> Async @ List`

ought to be defined, by waiting for all asynchronous calls to return their values before gathering
them in a list. Such commutation relations give rise to `monad transformers`_.

.. _monad transformers: https://en.wikipedia.org/wiki/Monad_transformer

