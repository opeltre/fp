from fp.meta Type, ArrowFunctor, HomFunctor

import fp.io as io


class Arrow(Type, metaclass=ArrowFunctor):
    """
    Default method implementations for Hom instances. 
    """
    
    class instance(metaclass=Type):

        src: Type
        tgt: Type
        
        def __new__(cls, *args, **kwargs) -> instance:
            arr = super().__new__(cls)
            arr.__init__(*args, **kwargs)
            return arr

        def __matmul__(self, other):
            return self._head_.compose(other, self)
 
        def __set_name__(self, owner, name):
            self.__name__ = name

    @classmethod
    def new(cls, A, B):

        class Arr_AB(cls.instance):
            src = A
            tgt = B

        return Hom_AB

    @classmethod
    def fmap(cls, phi):
        return lambda f: cls.compose(f, phi)

    @classmethod
    def cofmap(cls, psi):
        return lambda f: cls.compose(psi, f)

    @classmethod
    def _get_name_(cls, A, B):
        names = (A.__name__, B.__name__)
        return ' -> '.join(names)


# Hom type implementation
class Hom(Arrow, metaclass=HomFunctor):
    
    class instance(Arrow.instance):

        src: Type
        tgt: Type
        arity: int
        
        def __init__(self, pipe: Callable | tuple[Callable]): 
            self._pipe = pipe if isinstance(pipe, tuple) else (pipe,)
            if callable(pipe):
                self.__name__ = (pipe.__name__ if pipe.__name__ != "<lambda>" else "λ")
        
        def __call__(self, x:src) -> tgt:
            for f in self._pipe:
                x = f(x)
            return io.cast(x, self.tgt)
        
        def __lshift__(self, x:src) -> tgt:
            return self(x)
        
        def __rshift__(self, other):
            return self._head_.compose(self, other)

        def __repr__(self):
            if hasattr(self, '__name__'):
                return self.__name__
            name_one = lambda f: f.__name__ if f.__name__ != '<lambda>' else "λ"
            if len(self._pipe) < 4:
                return ' . '.join(name_one(f) for f in self._pipe[::-1])
            else:
                tail, head = self._pipe[0], self._pipe[-1]
                return name_one(head) + ' . (...) . ' + name_one(tail)
        
    @classmethod
    def compose(cls, f, *fs):
        src = f.src
        tgt = (fs[-1] if len(fs) else f).tgt
        pipe = sum((list(fi._pipe) for fi in (f, *fs)), [])
        io.assertComposable(f, *fs)
        return cls(src, tgt)(tuple(pipe))

    @classmethod
    def eval(cls, x, f):
        return f(x)


Type.Hom = Hom
