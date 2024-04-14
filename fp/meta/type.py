from .kind import Kind
import fp.io
import colorama

colorama.init()


class TypeClass(type, metaclass=Kind):
    """
    Base type class.

    This metaclass is used to define new type instances.
    Although all types do not inherit from `fp.Type`, they are all
    instances of `fp.meta.TypeClass` (same relationship as `abc.ABC` and
    `abc.ABCMeta`).
    """

    kind = "*"

    def __new__(cls, name, bases=(), dct={}, head=None, tail=None):
        """Create a new type."""
        T = super().__new__(cls, name, bases, dct)
        # expression tree for pattern matching 
        T._head = name if isinstance(head, type(None)) else head
        T._tail = tail
        # pretty print type annotations
        T.__str__ = cls.str_method(T.__str__)
        T.__repr__ = cls.repr_method(T.__repr__)
        #### cast?
        if not "cast" in dir(T):
            T.cast = cls.cast_method(T)
        ####
        return T
    
    @staticmethod
    def repr_method(rep):
        def _rep_(x):
            tx = f"{type(x)} : "
            indent = len(tx)
            rx = rep(x)
            tx = colorama.Style.DIM + tx + colorama.Style.NORMAL
            if rx[: len(tx)] == tx:
                return rx
            else:
                return tx + rx.replace("\n", "\n" + " " * indent)

        return _rep_

    @staticmethod
    def str_method(show):
        return lambda x: show(x)
    
    #### 
    @staticmethod
    def cast_method(T):

        def _cast_(x):
            if isinstance(x, T):
                return x
            try:
                Tx = T(x)
                return _cast_(Tx)
            except:
                raise fp.io.CastError(T, x)

        return _cast_
    ####

    def __repr__(self):
        """Show type name."""
        return f"{self.__name__}"


# --- Type variables ---


class Variable(TypeClass):

    def __new__(cls, name, head=None, tail=None):
        A = super().__new__(cls, name, (), {})
        A._head = name if isinstance(head, type(None)) else head
        A._tail = tail
        return A

    def __init__(A, name, head=None, tail=None): ...

    def match(A, B):
        """Matches `{"Ai": Type}` against a concrete type B."""
        # --- leaf node ---
        if A._tail == None:
            return {A.__name__: B}
        if not "_head" in dir(B):
            return None

        # --- head of expression ---
        out = {} if not isinstance(A._head, Variable) else {A._head.__name__: B._head}

        # --- tail of expression
        if len(A._tail) == len(B._tail):
            for Ai, Bi in zip(A._tail, B._tail):
                if isinstance(Ai, Variable):
                    mi = Ai.match(Bi)
                    if mi == None:
                        return None
                    out |= mi
                elif Ai != Bi:
                    return None
            return out
        return None

    def substitute(A, matches):
        """Return concrete type obtained by substitution of matches."""
        if A._tail == None:
            return matches[A.__name__]
        head = (
            A._head if not isinstance(A._head, Variable) else matches[A._head.__name__]
        )
        tail = []
        for Ai in A._tail:
            tail.append(Ai.substitute(matches) if isinstance(Ai, Variable) else Ai)
        return head(*tail)


class Constructor(Variable):

    def __call__(F, *Bs):
        """Apply constructor to type variables or concrete types."""
        Bs = [Variable(B) if isinstance(B, str) else B for B in Bs]
        name = f'{F.__name__}({", ".join(B.__name__ for B in Bs)})'
        FB = Variable(name, head=F, tail=Bs)
        return FB


# --- Instances ---


class Type(metaclass=TypeClass):

    pass
