Quickstart 
===========

This guide will walk you through the primitive types and basic functional 
patterns used by the `fp`_ library. 
See `here for all install options <installation.html>`_, or just 
get the latest `fp`_ release with::

    pip install funprogram

.. _fp: https://github.com/opeltre/fp

Primitive Types
---------------

Within `fp`, types are instances of the base `Type` metaclass. 
Subclasses of `Type` -- what Haskellers would call *type classes* -- 
describe types carrying more structure.
For instance `Monoid`, `Ring`, `List`, ...  are all 
subclasses of `Type` (in particular `List` is not an instance, it is actually a subclass 
of `Monoid`).

This does not prevent from using vanilla `type` subclasses 
(e.g. `str`, `int`, `float`...) in many places, as source types of
callables, or as arguments of type constructors. 
This is how `fp` actually manages to leverage on python builtins and useful external classes 
(e.g. `np.ndarray`, `jax.Array`, `torch.Tensor`, ...).

Numbers
^^^^^^^

The definition of the primitive type `fp.Int` is thus fairly succinct:

.. code-block:: python

    # fp/instances/num.py

    class Int(int, metaclass=Ring):

        def __str__(self):
            return super().__repr__()

In this case it is the `Ring` metaclass, 
subclassing `Type`, that takes care of implementing algebraic methods 
`add`, `sub` and `mul`. For floating-point number types, 
the `Alg` metaclass further implements the 
algebraic method `div` (understood element-wise for tensors, as in numpy and other backends).
These binary algebraic methods are automatically constructed as typed functions (described in 
more detail below) with `currying`_ support:

.. _currying: https://wikipedia.org/wiki/currying

.. code-block:: python

    >>> circ = Float.mul(3.14159265)
    >>> circ
    Float -> Float : mul 3.14159265
    >>> circ(2)
    Float : 6.2831853
    >>> circ.tgt
    Alg : Float
    >>> issubclass(Float, float) and isinstance(Float, Type)
    True
    >>> circ(2) == 2 * 3.14159265
    True

Strings
^^^^^^^

Similarly, the primitive type `Str` is just a `Monoid` instance 
(`+` operation) inheriting from the `str` builtin: 

.. code-block:: python

    >>> greet = Str.add("Hello ")
    >>> greet("World!")
    Str : 'Hello World!'
    >>> Str.add("Hello ", "World!")
    Str : 'Hello World!'
    >>> isinstance(Str, Monoid) and isinstance(Str, Type)
    True

The `Str` type currently does not implement very useful methods other than `+`.
It might be later enriched with lifts from the builtin `str` or links
to the `re` module.

Lists
^^^^^
Note that the `List` type constructor is **not** a `Type` instance 
inheriting from the builtin `list`. 

It is the so-called *top-type* `List.Object` that inherits from `list` instead, 
and gets equipped by the monoidal concatenation operation `add`, 
so that every `List`-type implements `add` by inheritance.

.. code-block:: python

   >>> isinstance(List, Type)
   False
   >>> issubclass(List, Monoid) and issubclass(List, Type)
   True
   >>> isinstance(List('A'), List) and isinstance(List('A'), Monoid)
   True
   >>> issubclass(List('A'), list) and issubclass(List('A'), List.Object)
   True

The `List('A')` type is a first example of *polymorphic* type, constructed by the 
`List` *functor* and *monad*. Any concrete type (including vanilla python types) 
may be passed to the `List` constructor, e.g. 
   
.. code-block:: python

    >>> List(Str).add(["Haskell Curry"])("Ada Lovelace", "Charles Babbage"])

    List Str : ['Haskell Curry', 'Ada Lovelace', 'Charles Babbage'])


Function Types
--------------
Before delving into the 
vast subject of functors and monads, we need to introduce the most important functor of all 
-- the `Hom` functor declaring callable types. 

Declaration
^^^^^^^^^^^
Typed functions -- also called *morphisms* -- from a source type `A` to a target type `B`
are constructed with the `Hom(A, B)` decorator.

.. code-block:: python

   @Hom(Int, Str)
   def bar(n: Int) -> Str:
        return "|" * n

The example above declares a typed function `bar` with implicit type casts 
to its `src` and `tgt` attributes:

.. code-block:: python

   >>> bar
   Int -> Str : bar
   >>> bar.src, bar.tgt
   (Ring : Int, Monoid : Str)
   >>> bar(12)
   Str : '||||||||||||'

An important feature of functional languages consists in a variety of programming
patterns aimed at providing a seamless user experience for function declaration.
The most elementary ones are descirbed below. 

Composition
^^^^^^^^^^^
The first such pattern is function composition, which is called by
the `__matmul__` operator: 

.. code-block:: python

   >>> foo = bar @ Int.mul(3)
   >>> foo
   Int -> Str : bar . mul 3
   >>> foo(2)
   Str : '||||||'
   >>> baz = Str.add("*!*") @ foo
   >>> baz(1)
   Str : '*!*|||'

Internally, the *top-type* `Hom.Object` stores a tuple or *pipe* of callables. 
This is made so that composition can be effectively associative, 
i.e. for every triple of morphism `f, g, h` we have

.. code-block:: python

   >>> f @ (g @ h) == (f @ g) @ h
   True

by comparing the underlying tuple instances. To compose an arbitrary number of functions 
in *pipe* order (as `nn.Sequential` would do), use `Hom.compose(*fs)` or simply pass a tuple
of python callables as argument to a `Hom` instance constructor:

.. code-block:: python

   >>> baz = Hom.compose(Int.mul(3), bar, Str.add("*!*"))
   >>> baz = Hom(Int, Str)((lambda n: n * 3, bar, lambda s: "*!*" + s))

Currying
^^^^^^^^

Functions of multiple variables can simply be typed by passing a tuple of 
types as source argument: 

.. code-block:: python

   @Hom((Str, Int), Str)
   def mul(s:Str, n:Int) -> Str:
       return s * n

Within `fp`, automatic `currying`_ of an n-ary function `f` will then return
a partially applied (n-k)-ary callable 
when `f` is called with only k arguments (see `functools.partial`).

.. _currying: https://wikipedia.org/wiki/currying

.. code-block:: python

   >>> f = Str.add("=>") @ mul(".") @ Int.mul(3)
   >>> f(3)
   Str : '=>.........'


Composite Types
---------------

The `struct` decorator provides a dataclass-like feature 
for declaring composite types:

.. code-block:: python

    @struct
    class User:
        name: Str
        email: Str
        pwd: Str = "0000"

    alice = User("Alice", "alice@company.io")
    bob = User("Bob", "bob@hotmail.fr", pwd='A+B=<3')

The `struct` decorator takes care of calling the `Struct` functor with appropriate 
keys and values arguments, by reading from the class annotations. 

Note that `Struct` instances are not extensible, i.e. they implement `__slots__` instead of 
`__dict__`. Trying to assign new fields will therefore raise an `AttributeError`: 

.. code-block:: python

    >>> bob.pizza = 'Hawaian'
    Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
    AttributeError: 'User' object has no attribute 'pizza'

Fields
^^^^^^

Fields of `Struct` types return typed getters of the form:

.. code-block:: python

   >>> User.name 
   User -> Str : .name
   >>> User.pwd(bob)
   Str : 'A+B=<3'

Note that this is taken care of by implementing fields as python descriptors 
that inherit from `Hom`. Having (in-place/out-of-place) setters accessible from
these descriptors should be available in a future release.

Inheritance
^^^^^^^^^^^

Children `Struct` types can be defined in a usual manner, e.g. 

.. code-block:: python
    
    >>> @struct
    ... class Admin(User):
    ...      pwd: Str = '1234'
    ...      pizza: Str = "Quatro Staggioni"
    
    >>> Admin.pizza
    Admin -> Str : .pizza

Any subclass defined this way can be used in place of its parent:
    
.. code-block:: python

    >>> List(User).fmap(User.pwd)([alice, bob, Admin("Charlie", "charlie@fp.co")])
    List Str : ['0000', 'A+B=<3', '1234']

More `Struct` features should be available in future releases of the package.

Tensor Types
------------

For now, `fp` exposes different kinds of tensor types:

* untyped `Tensor` types, with three backend-specific interfaces `Numpy`, `Jax` and `Torch`. 
* typed `Tens(*ns)` types, constructed with the `Tens` functor and inheriting from `Tensor`. 

Please note that the current behaviour is that `Tensor` is a dummy alias of `Torch`. 
This will change once the global backend state is properly integrated into 
the `Tensor` class.

See the `Tens Category <tens.html>`_ page for more details on how tensors are handled in `fp`. 
