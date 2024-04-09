from .type import Type, TypeClass
from .functor import BifunctorClass, NFunctorClass


class Prod(metaclass=NFunctorClass):

    def __new__(cls, *As):

        class Prod_As(tuple, metaclass=TypeClass):

            types = As

            def __new__(cls, *xs):
                if len(xs) != len(cls.types):
                    raise TypeError(
                        f"Invalid number of terms {len(xs)} "
                        + f"for {len(cls.types)}-ary product."
                    )

                def cast(A, x):
                    return x if isinstance(x, A) else A.cast(x)

                elems = [cast(A, x) for A, x in zip(cls.types, xs)]
                return super().__new__(cls, elems)

            def __init__(self, *xs):
                pass

            def __repr__(self):
                return "(" + ", ".join([str(x) for x in self]) + ")"

            @classmethod
            def cast(cls, *xs):
                def cast_one(A, x):
                    if isinstance(x, A):
                        return x
                    if "cast" in dir(A):
                        return A.cast(x)
                    return A(x)

                ys = [cast_one(A, x) for A, x in zip(cls.types, xs)]
                return cls(*ys)

        return Prod_As

    def __init__(self, *As):
        pass

    @classmethod
    def fmap(cls, *fs):

        src = cls((f.src for f in fs))
        tgt = cls((f.tgt for f in fs))

        @Arrow(src, tgt)
        def map_f(*xs):
            return tgt(*(f(x) for x, f in zip(xs, fs)))

        map_f.__name__ = "(" + ", ".join((f.__name__ for f in fs)) + ")"
        return map_f

    @classmethod
    def name(cls, *As):
        names = [A.__name__ for A in As]
        return f"({', '.join(names)})"


class ArrowClass(BifunctorClass):
    """
    Type constructor for arrow bifunctors.

    An `Arrow(A, B)` object f implements:

        f.src        = A
        f.tgt        = B

        f.__matmul__ : Arrow(B, C) -> Arrow(A, C)

        f.arity      : Int (default 1)

    Arrows of a concrete category moreover
    implement a `.__call__` method.
    """

    def __new__(cls, name, bases, dct):
        Arr = super().__new__(cls, name, bases, dct)
        Arr.curry = cls.curry_method(Arr)
        if not "__matmul__" in dir(Arr):
            Arr.__matmul__ = cls.matmul_method(Arr)
        return Arr

    @staticmethod
    def source_type(arrow, xs):
        if "source_type" in dir(arrow.functor):
            return arrow.functor.source_type(arrow, xs)
        if len(xs) == arrow.arity:
            return arrow.src
        else:
            ts = arrow.src.types[: len(xs)]
            return Prod(*ts)

    @staticmethod
    def source_cast(Src, r, xs):
        if r == 1 and isinstance(xs[0], Src):
            return xs[0]
        elif r > 1 and all(isinstance(x, S) for x, S in zip(xs, Src.types)):
            return xs
        elif "cast" in dir(Src):
            return Src.cast(*xs)
        raise TypeError(f"Could not cast input")

    @staticmethod
    def target_type(arrow, xs):
        if "target_type" in dir(arrow.functor):
            return arrow.functor.target_type(arrow, xs)
        if len(xs) == arrow.arity:
            return arrow.tgt
        else:
            ts = arrow.src.types[len(xs) :]
            return arrow.functor(Prod(*ts), arrow.tgt)

    @staticmethod
    def target_cast(Tgt, y):
        if isinstance(y, Tgt):
            return y
        elif "cast" in dir(Tgt):
            return Tgt.cast(y)
        raise TypeError(f"Could not cast output")

    @staticmethod
    def target(arr, y):
        """Cast of output y."""
        if isinstance(y, arr.tgt):
            return y
        try:
            Ty = arr.tgt.cast(y)
            return Ty
        except:
            raise TypeError(f"Output of type {type(y)} " + f"not castable to {arr.tgt}")

    @staticmethod
    def curry_method(Arr):

        def curry(f, xs):
            """
            Curried function applied to n-ary input xs for n < arity.
            """
            if len(xs) < f.arity:
                ts = f.src.types[-(f.arity - len(xs)) :]
                src = tuple(ts) if len(ts) > 1 else ts[0]

                @Arr(src, f.tgt)
                def curried(*ys):
                    return f(*xs, *ys)

                curried.__name__ = f"{f.__name__} " + " ".join((str(x) for x in xs))
                return curried

            raise TypeError(
                f"Cannot curry {Arr.arity} function on " + f"{len(xs)}-ary input"
            )

        return curry

    @classmethod
    def new_method(cls, new):
        functor_new = super().new_method(new)

        def _new_(Arr, *As):
            TAB = functor_new(Arr, *As)
            if not '__call__' in dir(TAB):
                TAB.__call__ = cls.call_method(Arr)
            TAB.__matmul__ = cls.matmul_method(Arr)
            TAB.__name__ = Arr.name(*As)
            return TAB

        return _new_

    @classmethod
    def call_method(cls, Arr):

        def _call_(arrow, *xs):
            """
            Function application with type checks and curryfication.
            """
            f = arrow.call
            r = arrow.arity

            # --- Input and output types
            Src = cls.source_type(arrow, xs)
            Tgt = cls.target_type(arrow, xs)

            # --- Full application
            if len(xs) == arrow.arity:
                Tx = cls.source_cast(Src, r, xs)
                y = f(Tx) if len(xs) == 1 else f(*Tx)
                Ty = cls.target_cast(Tgt, y)
                return Ty

            # --- Curried section
            if len(xs) < arrow.arity:
                return Arr.curry(arrow, xs)

        return _call_ if cls.arity > 0 else (lambda arrow: None)

    @classmethod
    def matmul_method(cls, Arr):
        """ Composition of functions. """
        def getname(arr):
            return arr.__name__ if '__name__' in dir(arr) else '\u03bb'

        def _matmul_(self, other):
            """Composition"""
            # arrow
            if "tgt" in dir(other):
                if self.src == other.tgt:
                    comp = Arr.compose(self, other)
                    comp.__name__ = f"{getname(self)} . {getname(other)}"
                    return comp
                raise TypeError(
                    f"Uncomposable pair"
                    + f"{(self.src, self.tgt)} @"
                    + f"{(other.src, other.tgt)}"
                )
            # apply to input
            out = self(other)
            return out

        return _matmul_


class Arrow(metaclass=ArrowClass):

    def __new__(cls, A, B):

        class TAB(Type):

            functor = Arrow
            types = (A, B)

            if isinstance(A, type):
                src, tgt, arity = (A, B, 1)
            elif "__iter__" in dir(A):
                As = Prod(*A)
                src, tgt, arity = (As, B, len(As.types))
            else:
                raise TypeError(f"Source {A} is not a type nor an iterable of types")

            def __init__(self, f):
                if not callable(f):
                    raise TypeError(f"Input is not callable.")
                self.call = f
                if "__name__" in dir(f) and f.__name__ != "<lambda>":
                    self.__name__ = f.__name__
                else:
                    self.__name__ = "\u03bb"

            def __repr__(self):
                return self.__name__

        return TAB

    def __init__(self, A, B):
        pass

    @classmethod
    def compose(cls, f, g):
        """Composition of functions"""
        return cls(g.src, f.tgt)(lambda *xs: f(g(*xs)))

    @classmethod
    def name(cls, A, B):
        if isinstance(A, type) and isinstance(B, type):
            return f"{A.__name__} -> {B.__name__}"
        elif isinstance(A, (tuple, list)):
            input = " -> ".join(
                [Ak.__name__ if '__name__' in dir(A) else '*' for Ak in A])
            return f"{input} -> {B.__name__}"
        elif "__name__" in dir(A) and "__name__" in dir(B):
            return f"{A.__name__} -> {B.__name__}"
        return f"A -> B"
