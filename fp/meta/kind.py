from colorama import Fore

from .method import Method

from functools import cache
import fp.io as io

Args = tuple[int] | type(...) 

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
    _methods_ = []

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
        if T.__base__.__name__ == 'Var': 
            return None
        elif any(b.__name__ == 'Var' for b in T.__bases__):
            return None
        T._holes_ = {}
        # --- register methods
        for k, method in Method.list(cls):
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
            # skip if found
            if inherited: 
                #_doc_ += k + ": " + str(T._eval_signature_(method)) + "\n"
                continue
            # register hole and raise warning 
            sgn = T._eval_signature_(method)
            T._holes_[k] = sgn
            t, tc = T.__name__, type(T).__name__
            print(io.WARN, k, ":", sgn, f"missing in {t} <= {tc}")

    def _doc_(T):
        # document methods
        doc = T.__doc__ or ""
        try:
            cut = doc.find("\n\n")
            head, tail = (doc[:cut], doc[cut:]) if cut >= 0 else (doc, "")
            methods = T.methods().items()
            title = "Class Methods"
            title = "\n\n" + title + "\n" + "-" * len(title) + "\n\n"
            if tail[:len(title)] == title or not len(methods):
                return None
            Mdoc = title 
            for k, mk in T.methods().items():
                Mdoc += f"* {k} : `{mk}`  \n"
            doc = head + Mdoc.replace("\n", "\n    ") + tail
        except Exception as e:
            (e)
            raise e
        finally:
            T.__doc__ = doc

    def __repr__(self):
        """Show type name."""
        out = f"{self} : " + Fore.YELLOW + f"{self.kind}" + Fore.RESET
        out += f" ({type(self).__name__})"
        return out

    def __str__(self):
        return self.__name__
    
    def methods(T):
        """
        Method signatures.
        """
        methods = Method.list(T.__class__)
        return {k: T._eval_signature_(mk) for k, mk in methods}

    def _eval_signature_(T, method):
        """
        Used to wrap evaluation of signature.

        Override in subclasses with a reference to `Type.Hom`.
        """
        if hasattr(method, 'signature'):
            signature = method.signature
        try: 
            return signature(T)
        except:
            name = signature.__name__
            if not any(b.__name__ == 'Var' for b in T.__bases__):
                print(io.WARN, name, ": could not evaluate signature on", T)
            return signature
    
    def __init_subclass__(child, *xs, **ys):
        child._methods_ = []
        for m in super(child, child)._methods_:
            child._methods_.append(m)

    @staticmethod
    def _functor_kind_(r : int | type(...), cov: Args, contrav: Args) -> str:
        """
        Kind string of a functor. 
        """
        op = "ꜝ"
        # fixed and variable arity
        if r is ...:
            if cov is ...:
                return "(*, ...) -> *"
            if contrav is ...:
                return f"(*{op}, ...{op}) -> *"
            # varargs
            r = len(cov) + len(contrav) - 1
            args = ["*" * r] + ["..."]
        else: 
            # r-ary
            args = ["*" for _ in range(r)]
        op_args = contrav
        if op_args is ...:
            op_args = tuple(range(r))
        # tag contravariant arguments
        for i in op_args:
            if i is ...:
                args[-1] += op
            else:
                args[i] += op
        # add brackets conditionally
        if len(args) == 1:
            return args[0] + " -> *"
        return "(" + ", ".join(args) + ") -> *"
