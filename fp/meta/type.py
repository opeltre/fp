from .kind import Kind
import fp.io as io

class Type(type, metaclass=Kind):
    
    def __new__(cls, name, bases=(), dct={}, head=None, tail=None):
        """Create a new type expression."""
        T = super().__new__(cls, name, bases, dct)
        # expression tree for pattern matching 
        T._head_ = name if isinstance(head, type(None)) else head
        T._tail_ = tail
        # pretty print type annotations
        T.__str__ = io.str_method(T.__str__)
        T.__repr__ = io.repr_method(T.__repr__)
        return T
    
    def __repr__(self):
        """Show type name."""
        return f"{self.__name__}"


# --- Type variables ---

class Variable(Type):

    def __new__(cls, name, head=None, tail=None):
        A = super().__new__(cls, name, (), {})
        A._head_ = name if isinstance(head, type(None)) else head
        A._tail_ = tail
        return A

    def __init__(A, name, head=None, tail=None): ...

    def match(A, B):
        """Matches `{"Ai": Type}` against a concrete type B."""
        # --- leaf node ---
        if A._tail_ == None:
            return {A.__name__: B}
        if not "_head_" in dir(B):
            return None

        # --- head of expression ---
        out = {} if not isinstance(A._head_, Variable) else {A._head_.__name__: B._head_}

        # --- tail of expression
        if len(A._tail_) == len(B._tail_):
            for Ai, Bi in zip(A._tail_, B._tail_):
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
        if A._tail_ == None:
            return matches[A.__name__]
        head = (
            A._head_ if not isinstance(A._head_, Variable) else matches[A._head_.__name__]
        )
        tail = []
        for Ai in A._tail_:
            tail.append(Ai.substitute(matches) if isinstance(Ai, Variable) else Ai)
        return head(*tail)

    def __call__(F, *Bs):
        """Apply constructor to type variables or concrete types."""
        Bs = [Variable(B) if isinstance(B, str) else B for B in Bs]
        name = f'{F.__name__}({", ".join(B.__name__ for B in Bs)})'
        FB = Variable(name, head=F, tail=Bs)
        return FB

