from fp.meta import Type, NFunctor
import fp.io as io

class Prod(Type, metaclass=NFunctor):
    """
    Product functor.

    The type `Product(A, B, ...)` is a type-aware subclass of `tuple`.
    
    Example:
    --------
    .. code::

        >>> a, b = Str("abcd"), Int(8)
        >>> x = Prod(Str, Int)(a, b)
        >>> x
        (Str, Int) : ('abcd', 8)
        >>> @Hom(Int, Str)
        ... def bar(n): return n * "|"
        ...
        >>> Pf = Prod.fmap(Str.len, bar).show()
        (Str, Int) -> (Int, Str) : (len, bar)
        >>> Pf(x)
        (Int, Str) : (4, '||||||||')
    """
    
    class _top_(tuple):
        """
        Product base type: `tuple` alias.
        """
        def __new__(P, *xs):
            if len(xs) != len(P._tail_):
                raise TypeError(f"Got {len(xs)} terms in product type {P.__name__}")
            xs = [io.cast(x, A) for A, x in zip(P._tail_, xs)]
            return super().__new__(P, xs)

        def __init__(prod, *xs): ...

        def __repr__(self):
            return "(" + ", ".join(str(x) for x in self) + ")"

        @classmethod
        def cast(P, xs):
            if not isinstance(xs, P):
                return P(*(io.cast(x, A) for A, x in zip(P._tail_, xs)))
    
    def __init__(P, *As):
        ...

    @classmethod
    def fmap(cls, *fs):

        src = cls(*(f.src for f in fs))
        tgt = cls(*(f.tgt for f in fs))

        @Type.Hom(src, tgt)
        def map_f(xs):
            ys = tuple(f(x) for x, f in zip(xs, fs))
            return ys

        map_f.__name__ = "(" + ", ".join((f.__name__ for f in fs)) + ")"
        return map_f

    @classmethod
    def _get_name_(cls, *As):
        return "(" + ", ".join(A.__name__ for A in As) + ")"

    @classmethod
    def cast(cls, xs):
        if isinstance(xs, tuple):
            return cls(*xs)
        return io.cast(xs, cls)

Type.Prod = Prod
