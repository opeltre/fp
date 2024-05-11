from __future__ import annotations
from fp.meta import Type, ArrowFunctor

class Arrow(Type, metaclass=ArrowFunctor):
    """
    Default method implementations for Hom instances. 
    """
    
    src = Type
    tgt = Type

    class Object(metaclass=Type):

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
        TAB = super().new(A, B)
        TAB.src = A
        TAB.tgt = B
        return TAB

    @classmethod
    def compose(cls, f, g):
        return cls(f.src, g.tgt)()

    @classmethod
    def fmap(cls, phi):
        """
        Pushforward : post-composition on the target.
        """
        @Type.Hom(cls("X", phi.src), cls("X", phi.tgt))
        def push(f):
            return cls.compose(f, phi)
        push.__name__ = "push " + phi.__name__
        return push

    @classmethod
    def cofmap(cls, psi):
        """
        Pullback : pre-composition on the source.
        """
        @Type.Hom(cls(psi.tgt, "Y"), cls(psi.src, "Y"))
        def pull(f):
            return cls.compose(psi, f)
        pull.__name__ = "pull " + psi.__name__
        return pull

    @classmethod
    def _get_name_(cls, A, B):
        names = (A.__name__, B.__name__)
        return ' -> '.join(names)
