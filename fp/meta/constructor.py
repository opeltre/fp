from .kind import Kind
from .type import Constructor, Variable, Type, TypeClass
from .method import Method

from functools import cache

import fp.io as io

class ConstructorClass(type, metaclass=Kind):

    kind = "(*, ...) -> *"
    arity = ...

    @Method
    def new(cls):
        """Return a new type"""
        return Type, Type
    
    def __new__(cls, name, bases, dct):
        """
        Return a new type constructor.

        The class body of a type constructor instance `C` will be looked up for 
        methods whose signature has been registered with `@fp.meta.Method`. 

        In particular, the type instance `C` is expected to have a classmethod `C.new`returning 
        a class. It will be called from the actual `__new__` method of the constructor,
        which takes care of:
        - setting `_head` and `_tail` attributes of `C(*As)` as `C` and `As` respectively 
        for symbolic representation of type expressions, 
        - setting `C(*As)__name__` as the output value of `C.name(*As)`.
        - returning a `Variable` instance if any argument is a variable.
        """
        # --- enforce TypeClass inheritance
        #if not any(isinstance(B, type) for B in bases):
        #    bases = (TypeClass, *bases)
        constructor = super().__new__(cls, name, bases, dct)

        # --- register methods
        for k, v in Method.list(cls):
            if k in dct:
                method = dct[k]
                setattr(constructor, k, method)
            elif any(hasattr(base, k) for base in bases):
                continue
            else:
                print(f"Missing method {k}: {constructor.__name__} <= {cls.__name__}")

        # --- decorate constructor.new

        @cache
        def new(T, *As, **Ks):

            def check_nargs(cls, As):
                if cls.arity is not ... and cls.arity - len(As) != 0:
                    raise TypeError(
                        f"Wrong kind : could not apply {cls.arity}-ary "
                        + f"functor {cls} to input {As}"
                    )

            def parse_variables(cls, As):
                As = tuple(Variable(A) if isinstance(A, str) else A for A in As)
                var = any(isinstance(A, Variable) for A in As)
                return As, var

            check_nargs(cls, As)
            As, var = parse_variables(cls, As)
            # inherit from T.new(*As)
            TA = T.new(*As, **Ks)
            # get __name__
            TA.__name__ = T.name(*As)
            # symbolic (T)::(*As) ---
            TA._head = T
            TA._tail = tuple(As)
            # return variable if one input is a variable
            if var:
                return Variable(TA.__name__, TA._head, TA._tail)
            T.__init__(TA, *As, **Ks)
            return TA
        
        constructor.__new__ = new
        
        # return initialized instance
        cls.__init__(constructor, name, bases, dct)
        return constructor
    
    def __init__(T, name, bases, dct):
        """
        Initialize a constructor class.

        Override to append methods on the returned types.
        """
        super().__init__(name, bases, dct)

    def name(T, *As):
        """
        Return `__name__` string of output type.

        Override as a classmethod from `ConstructorClass` instances as needed.
        """
        names = [A.__name__ if "__name__" in dir(A) else str(A) for A in As]
        tail = ", ".join(names)
        return f"{T.__name__} ({tail})" if len(names) > 1 else f"{T.__name__} {tail}"
    
    def methods(T):
        """
        Return method signatures of T.
        """
        methods = Method.list(type(T))
        return {k: ' -> '.join(map(str, mk.signature(T))) for k, mk in methods}

    @classmethod
    def _base(cls):
        return Type
