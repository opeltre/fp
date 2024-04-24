from __future__ import annotations
from fp.meta import Type, ArrowFunctor

class Arrow(Type, metaclass=ArrowFunctor):
    """
    Default method implementations for Hom instances. 
    """
    
    src = Type
    tgt = Type

    class _top_(metaclass=Type):

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
        return lambda f: cls.compose(f, phi)

    @classmethod
    def cofmap(cls, psi):
        return lambda f: cls.compose(psi, f)

    @classmethod
    def _get_name_(cls, A, B):
        names = (A.__name__, B.__name__)
        return ' -> '.join(names)
