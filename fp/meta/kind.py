from colorama import Fore

from .method import Method

from functools import cache

   
class Kind(type):
    """
    Type kinds.

    Subclasses of `Kind` may register class method signatures with 
    the `@Method` decorator, e.g. 


        >>> class Functor(Type):
        ...
        ...     @Method
        ...     def fmap(F):
        ...         return Hom('A', 'B'), Hom(F('A'), F('B'))
    """
    
    kind = "*"

    def __new__(cls, name, bases, dct):
        """Create a kind."""
        T = super().__new__(cls, name, bases, dct)
        T.__str__ = lambda t: t.__name__ if hasattr(t, "__name__") else "?"
        T.__repr__ = lambda t: (
            Fore.MAGENTA + f"{type(t)} : " + Fore.RESET + T.__str__(t)
        )
        cls._check_methods_(T, bases, dct)
        return T
    
    @classmethod
    def _check_methods_(cls, T, bases, dct):
        """
        Check that declared class methods are defined.

        Called by `Kind.__new__` to explicitly call setattr as needed.
        """
        # --- register methods
        for k, v in Method.list(cls):
            # explicit dct definition 
            if k in dct:
                method = dct[k]
                setattr(T, k, method)
                continue
            # look for default implementation in bases
            inherited = False
            for base in bases:
                if hasattr(base, k):
                    setattr(T, k, getattr(base, k).__get__(T, T.__class__))
                    inherited = True
                    break 
            # raise warnings
            if inherited: 
                continue
            t, tc = T.__name__, type(T).__name__
            print(f"! Missing method {k} : {v.signature} in {t} <= {tc}")

    def __repr__(self):
        """Show type name."""
        return f"{self} : " + Fore.YELLOW + f"{type(self).kind}" + Fore.RESET

    def __str__(self):
        return self.__name__
    
    def methods(T):
        """
        Method signatures.
        """
        methods = Method.list(T.__class__)
        return {k: ' -> '.join(map(str, mk.signature(T))) for k, mk in methods}
