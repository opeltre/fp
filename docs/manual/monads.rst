Monads
------
Monads are a very powerful abstraction of the intuitive and ubiquitous notion of 
*composition*. This includes many binary operators from algebra, from much more subtle 
and general examples of great use for writing programs. 
Two (or more) consecutive lines of code may indeed be thought as *composed* 
with one another, while the actual behaviour 
of composition may depend on a varying context
(environment, I/O, error handling, asynchronicity...).

Again, `List` remains the canonical example of a monad in functional programming.
This explains why a lot of online content may describe functors and monads as "abstract containers".
We prefer to emphasize their actual generality right away, although keeping the lists example 
in mind is always useful. 

But monads are also a generalisation of the ubiquitous definition of `monoids`_, which may now 
be scholarly defined as categories with a single object • and a set M of morphisms m : • → • 
(groups are a particular case, including morphism inversions), although every day examples 
are just (**N**, +) or (**R**, *). 

Endofunctors 
^^^^^^^^^^^^
In category theory, a *monad* is synonym for "a monoid in the (monoidal) category of 
endofunctors". This is a rather pedantic way to express the following important facts. 

* Given a category `C`, any two functors `M : C -> C` and `M' : C -> C` may be *composed* to 
  form a functor `M' @ M`. This composition is *associative* (monoidal operation). 

* Such *endofunctors* of `C` moreover form the objects of a category 
  with `natural transformations`_ as morphisms (see below), 

* Given an endofunctor `M : C -> C`, a natural transformation `unit : Id -> M`
  might define a *unit element* in `M`,

* Given an endofunctor `M : C -> C`, a *natural transformation* `join : M @ M -> M`
  might define a *composition* in `M`.
 
.. _natural transformations: https://en.wikipedia.org/wiki/Natural_transformation 

In functional programming, almost all functors encountered 
are *endofunctors* of the `Type` category, and may therefore be composed with one another.

In practice, a monad is therefore any type endofunctor implementing the following
`Method` instances:

* `unit : A -> M(A)` for every type `A`, 
* `join : M(M(A)) -> M(A)` for every type `A`.

We provide details on each of these operations and the associated `bind` method below.

Unit
^^^^
A monad's unit promotes (wraps) any value `x : A` 
to a *monadic value* `M.unit(x) : M(A)`. 
The `List` unit, for instance, simply maps any `x : A` to the singleton 
list `[x] : List(A)`.

The `IO` monad of Haskell-like languages, in contrast, will promote any value `x : A` 
to an I/O operation called `return x : IO(A)`. 
This *monadic value* doesn't actually perform any I/O, 
but allows to terminate any sequence of I/O operations 
with the output value `x`: remember that the purpose of monadic values is to be *composed*!
This example might thus be transposed to many different contexts 
(asynchronicity, error-handling, etc.) 
and *unit* and *return* are often synonyms in functional programming. 

Join
^^^^
Just like composition in a monoid consists of a function (set morphism) 
`M x M -> M`, *monadic composition* is embodied by a natural transformation 
(functor morphism) `join : M @ M -> M`. When translating from the category of sets to 
the category of functors, the cartesian product is replaced by functor composition 
(these so-called *monoidal operations* are both associative, with a unit operation: 
point-set and identity functor respectively). 

In practice, this means that for every type `A`, the twice-monadic type `M(M(A))` can be 
*flattened* to the monadic type `M(A)`. The most simple example of such a flattening 
is obtained by joining a list of lists together with `List.join`.

Now what does it mean to *join* more general monadic types? Let us emphasize once more 
that lists and containers are not what makes monads interesting... 
It's the abstract notion of *program composition* that makes them so powerful. 

Assume that `M(A)` denotes a type of programs that return a value of type `A`. 
Then `M(M(A))` is the type of a program *that returns another program* whose return type 
is `A`. In order to map `M(M(A))` to `M(A)`, one simply needs to transform the 
parent program by executing the returned child program!

Bind
^^^^
Monads are often equivalently defined by their so-called `bind` operation, 
more commonly used in practice, although less straightforward as an axiom. 
Its signature is: 

* `bind : (A -> M(B)) -> M(A) -> M(B)`

Note how `bind` has a very similar signature to that of `fmap`. 
*binding a monadic function* `f : A -> M(B)` is actually done by first mapping it 
through through the monadic functor, `M.fmap(f) : M(A) -> M(M(B))`, 
before flattening its output with `M.join`. 
Although this always yields a default implementation of `bind` provided `join` is defined, 
more efficient implementations might be provided. 

Assume for instance `M(A)` denotes the type for a *promise* valued in `A` 
(asynchronous programming). Then `A -> M(B)` denotes the type of an asynchronous 
function returning in `B`, and `M.bind` simply provides the typed way to pipe asynchronous 
functions. 

**Q:** how would you define `join` in terms of `bind`?
 
Examples
^^^^^^^^
Many important monad examples are conceptually similar to what 
the Haskell `IO` monad does, so that understanding how `IO` behaves is very useful, even 
though monadic abstraction of I/O operations is not necessary in an effectful language like Python.
As examples of such "programmatic" monads, let us mention: 

* the `State S` monad, mapping every `A` to the type `S -> (S, A)` (stateful computation),
* the `Reader E` monad, mapping every `A` to the type `E -> A` (environment dependent computation),
* the `Async` monad, mapping every `A` to a *promise* for a value in `A` 

and many different variations of the above. In these examples, `bind` describes a way to chain 
individual programs together, depending on some kind of (evolving) context, while `join`  
executes any child programm returned by a parent program.

As a different yet just as important example, given any *monoid* `M`
(e.g. `Int`, `Str` or `List[a]`),

* the `Writer M` monad maps every type `A` to the type `(M, A)` (annotated value). 
  the twice-monadic type `(M, (M, A))` is flattened by to `(M, A)` by the monoidal 
  (i.e. associative) composition in `M`. 

`Writer monads`_ (and functors) are essential for error-handling in functional languages: 
the `Writer Str` functor lifts values and pure (total) functions by appending an empty traceback,
while the monad's `bind` method chains monadic functions (returning traced values) by 
concatenating tracebacks. 
Tracing program execution is however not restricted to error-handling (e.g. profiling, 
model training and evaluation) and usecases for writer monads are ubiquitous.

.. _group: https://wikipedia.org/wiki/group_(mathematics)
.. _partial order: https://wikipedia.org/wiki/partially_ordered_set
.. _monoids: https://wikipedia.org/wiki/monoid
.. _Writer monads: https://wikipedia.org/wiki/writer_monad
