import inspect
#import fp.meta.type 

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
            a python descriptor with `__dict__` lookup on type instances.
            Warnings will be printed upon class instance creation 
            for any missing method implementations.

    Example:
    --------
    
    .. code-block::

        # Type class `Eq` with a single method `eq : a -> a -> Bool`
        >>> class Eq(fp.Type):
        ...
        ...     @fp.Method
        ...     def eq(a):
        ...         return fp.Hom((a, a), fp.Bool)
    """

    def __set_name__(self, owner, name):
        self._name = "_" + name
        self.name = name

    def __init__(self, signature):
        self.signature = signature
        self.__doc__ = signature.__doc__

    def __get__(self, obj, objtype=None):
        if obj is not None:
            return getattr(obj, self._name)
        else:
            return self

    def __set__(self, obj, value):
        setattr(obj, self._name, value)
    
    @classmethod
    def list(cls, objtype):
        """
        List method names and signatures defined on a type class.

        Note:
        -----
        Methods appear in alphabetical order. It would be more
        understandable if they appeared in the order they were 
        created. 
        """
        return inspect.getmembers(objtype, lambda x: isinstance(x, cls))
