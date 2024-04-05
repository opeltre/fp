from .kind import Kind
from .type import Type, TypeMeta, TypeVar, Variable, Constructor

import fp.io


def decorate(method):
    def decorator(f):
        return lambda *xs, **ks: f(method, *xs, **ks)

    return decorator


class Method:

    def __set_name__(self, owner, name):
        owner._methods = owner._methods if "_methods" in dir(owner) else {}
        owner._methods[name] = self.signature
        self._name = "_" + name
        self.name = name

        def register(method):
            print(f"register {method.__name__}")
            self.__set__(owner, lambda x: method(owner, x))

        setattr(owner, self._name, register)

    def __init__(self, signature):
        self.signature = signature

    def __get__(self, obj, cls=None):
        M_obj = self.signature(obj)
        print(f"--> Method:\n {obj}\n{M_obj}")
        if obj is not None:
            return getattr(obj, self._name)
        if self._name in dir(cls):
            return getattr(cls, self._name)
        return self.signature(Constructor("T"))

    def __set__(self, obj, value):
        print(f"===> Method:\n {obj}\n {value}")
        setattr(obj, self._name, value)


class ConstructorMeta(Kind):

    kind = "* -> *"
    arity = 1

    def __new__(cls, name, bases, dct):
        """Methods"""
        T = super().__new__(cls, name, bases, dct)

        @decorate(T.__new__)
        def new(_new_, func, *As, **Ks):
            """Functorial type constructor"""
            TA = _new_(func, *As, **Ks)
            # --- symbolic (T)::(*As) ---
            TA._head = func
            TA._tail = tuple(As)
            return TA

        T.__new__ = new
        return T


class FuncMeta(ConstructorMeta):

    @Method
    def new(cls):
        return Hom(Type, Type)

    @Method
    def fmap(cls):
        T = cls if callable(cls) else Constructor("T")
        return Hom(Hom("A", "B"), Hom(T("A"), T("B")))

    def __matmul__(F, G):
        """Composition of functors."""

        class FG(Func):

            kind = G.kind
            arity = G.arity
            src, tgt = G.src, F.tgt

            def __new__(cls, *As, **Ks):
                return F(G(*As, **Ks))

            @classmethod
            def fmap(cls, f):
                return F.fmap(G.fmap(f))

        FG.__name__ = f"{F.__name__} @ {G.__name__}"
        return FG


class MonadMeta(FuncMeta):

    def methods(M):
        return dict(
            unit=Method("A", M("A")),
            join=Method(M(M("A")), M("A")),
            bind=Method(Hom("A", M("B")), Hom(M("A"), M("B"))),
        )


# -----------------


class Func(TypeMeta, metaclass=FuncMeta):
    """Functor type class."""

    kind = "* -> *"
    arity = 1
    src, tgt = Type, Type

    fmap = Method(lambda T: Hom(Hom("A", "B"), Hom(T("A"), T("B"))))

    def __new__(cls, *As):
        name = cls.name(*As)
        bases = (cls.new_type(*As),)
        TA = super().__new__(cls, name, bases, {})
        cls.__init__(TA, *As)
        return TA

    def __init__(TA, *As):

        def map(x, f, tgt=None):
            T = TA.__class__
            if not isinstance(f, T.src.Hom):
                src = TA._tail if T.arity != 1 else TA._tail[0]
                f = T.src.Hom(src, tgt)(f)
                return T.fmap(f)(x)
            return T.fmap(f)(x)

        TA.map = map

    @classmethod
    def name(cls, *As):
        names = [A.__name__ if "__name__" in dir(A) else str(A) for A in As]
        tail = ", ".join(names)
        return (
            f"{cls.__name__} ({tail})" if len(names) > 1 else f"{cls.__name__} {tail}"
        )

    @classmethod
    def new_type(cls, *As):
        return Type


class Monad(Func):

    @classmethod
    def join(cls): ...


class BiFunc(Func):

    kind = "(*, *) -> *"
    arity = 2


class NFunc(Func):

    kind = "(*, ..., *) -> *"
    arity = -1


# -------------------


class Prod(NFunc):

    @classmethod
    def new_type(cls, *As):

        class Prod_As(tuple):

            def __new__(P, *xs):
                xs = [A(x) for A, x in zip(P._tail, xs)]
                return super().__new__(P, xs)

            def __init__(prod, *xs): ...

            def __repr__(self):
                return "(" + ", ".join(str(x) for x in self) + ")"

            @classmethod
            def cast(P, xs):
                if not isinstance(xs, P):
                    return P(*(A.cast(x) for A, x in zip(P._tail, xs)))

        return Prod_As

    @classmethod
    def name(cls, *As):
        return "(" + ", ".join(A.__name__ for A in As) + ")"


class Hom(BiFunc):

    @classmethod
    def new_type(cls, A, B):

        class Hom_AB:
            src, tgt = A, B

            def __new__(cls, f):
                if isinstance(f, Hom):
                    return f
                self = super().__new__(cls)
                self.call = f
                return self

            def __call__(self, *xs, **ks):
                y = self.call(*xs, **ks)
                return y if self.tgt is None else self.tgt.cast(y)

        return Hom_AB


Type.Hom = Hom
