import unittest

from fp import Type, Type, Functor, Hom

A = Type("A", (), {})
f = Hom(A, A)(lambda x: x)


class TestFunctor(unittest.TestCase):

    def test_functor(self):

        class T(Functor):
            
            class Object(Type):
                ...

            @classmethod
            def fmap(cls, f):
                return f

        TA = T(A)
        result = isinstance(TA, type)
        self.assertTrue(result)

        Tf = T.fmap(f)
        result = isinstance(Tf, Hom(A, A))
        self.assertTrue(result)

        y = TA()
        result = T.fmap(f)(y)
        self.assertTrue(result == y)

        # type output equality
        self.assertTrue(TA == T(A))
