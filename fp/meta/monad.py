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
        
        @property
        def _monad_(ma):
            return ma._head_

        def bind(ma, mf):
            monad = ma._monad_
            return ma._monad_.bind(ma, mf)

        def __rshift__(ma, mf):
            return ma.bind(mf)
