import inspect


class TypeClassMethod:
    """
    Describe a type class by its method signatures.

    Use as a decorator to declare a method for a type class `MyClass <= TypeClass`

    This will register a `__dict__` lookup on type instances of `MyClass`,
    and allows for polymorphic typing on the class methods of type class instances.

    Parameters:
    -----------
        `signature (callable)`:
            a function `Type -> Type` accepting a type instance as argument,
            and returning the method's type.

    Returns:
    --------
        `method (TypeClassMethod)`:
            a python descriptor with `__dict__` lookup on type instances.
            Warnings will be printed upon class instance creation
            for any missing method implementations.

    Example:
    --------

    .. code-block::

        # Type class `Eq` with a single method `eq : a -> a -> Bool`
        >>> class Eq(fp.Type):
        ...
        ...     @fp.TypeClassMethod
        ...     def eq(a):
        ...         return fp.Hom((a, a), fp.Bool)
    """

    def __init__(self, signature):
        self.signature = signature
        self.__doc__ = signature.__doc__

    @classmethod
    def list(cls, objtype):
        """
        List method names and signatures defined on a type class.

        Note:
        -----
        TypeClassMethods appear in alphabetical order. It would be more
        understandable if they appeared in the order they were
        created.
        """
        out = []
        methods = objtype._methods_
        members = inspect.getmembers(objtype, lambda x: isinstance(x, cls))
        for k, _ in methods.items():
            for p, m in members:
                if k == p:
                    out.append((k, m))
        return out
