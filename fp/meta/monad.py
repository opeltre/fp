from .method import Method
from .type import Type
from .functor import Functor


class Monad(Functor):
    
    
    @Method
    def unit(cls):
        return 'A', cls('A')

    @Method
    def join(cls):
        return cls(cls('A')), cls('A')

    @Method
    def bind(cls):
        return (cls('A'), Type.Hom('A', cls('B'))), cls('B')

    class _defaults_(Functor._defaults_):

        @classmethod
        def bind(cls, ma, mf):
            mmb = cls.fmap(mf)(ma)
            return cls.join(mmb)

    class _instance_(Functor._instance_):

        def bind(ma, mf):
            monad = ma._head_
            return monad.bind(ma, mf)

        def __rshift__(ma, mf):
            monad = ma._head_
            return monad.bind(ma, mf)
