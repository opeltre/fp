from fp.meta import Type, Functor, Arrow

class Wrap(Functor):

    def __new__(cls, A):

        class Wrap_A (Type):

            def __init__(self, data):
                self.data = data
            
            def __repr__(self):
                return A.__str__(self.data)

        return Wrap_A

    @classmethod
    def fmap(cls, f):
        src, tgt = cls(f.src), cls(f.tgt)
        return Arrow(src, tgt)(
            lambda x: tgt(f(x.data))
        )
