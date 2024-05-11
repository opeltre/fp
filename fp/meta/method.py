class Method:
    """
    Method descriptor used as attribute to describe a type class.

    Use as a decorator to declare a method for a type class `MyClass <= TypeClass`

    This will register a `__dict__` lookup on type instances of `MyClass`,
    and allows for polymorphic typing on the class methods of the type instance.

    Parameters:
    -----------
        `signature (callable)`:
            a function `Type -> Type` accepting a type instance as argument,
            and returning the method's type.

    Returns:
    --------
        `method (Method)`:
            a python descriptor with __dict__ lookup on type instances.

    Example:
    --------

        # Type class `Eq` with a single method `eq : a -> a -> Bool`
        >>> class EqClass(fp.TypeClass):
        ...
        ...     @fp.Method
        ...     def eq(a):
        ...         return fp.Hom((a, a), fp.Bool)
    """

    def __set_name__(self, owner, name):
        owner._methods = owner._methods if "_methods" in dir(owner) else {}
        owner._methods[name] = self.signature
        self._name = "_" + name
        self.name = name

    def __init__(self, signature):
        self.signature = signature

    def __get__(self, obj, objtype=None):
        if obj is not None:
            return getattr(obj, self._name)
        elif self._name in dir(objtype):
            return getattr(objtype, self._name)

    def __set__(self, obj, value):
        setattr(obj, self._name, value)
