Quick start 
===========

This guide assumes you have successfully `installed <installation.html>`_
the `fp`_ package.

.. _fp: https://github.com/opeltre/fp

It will walk you through the basic types of the library and show 
how to use some of the functional features exposed by the framework. 


The `Type` Cartesian Category
-----------------------------

Type Objects
^^^^^^^^^^^^

All types within fp are instances of the metaclass `fp.meta.type.Type`, 
which for instance takes care of pretty-printing type annotations of 
typed values.::

    >>> from fp import *
    >>> isinstance(Int, Type)
    True
    >>> Int(8)
    Int : 8

The `Int` class is a subclass of the python builtin `int`. Its behaviour is 
only decorated by the metaclass `type(Int) == Ring`, a subclass of `Type`.::

    >>> fp = Int("fp", base=32)
    Int : 505
    >>> isinstance(fp, int)
    True
    >>> [isinstance(T, Type), for T in (Int, int)]
    [True, False]

Instances of `Type` are referred to as type *objects*, as `Type` forms 
a (cartesian) `category`_.

.. _category: https://wikipedia.org/category(mathematics)


