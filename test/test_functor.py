import unittest

from fp.meta import TypeMeta, Type, Functor, Arrow

A = TypeMeta("A", (), {})
f = Arrow(A, A)(lambda x: x)

class TestFunctor(unittest.TestCase):

    def test_functor(self):

        class T(Functor):

            def __new__(cls, A):
                return TypeMeta(f"T {A.__name__}", (A,), {})
            
            @classmethod
            def fmap(cls, f):
                return f
        
        TA = T(A)
        result = isinstance(TA, type)
        self.assertTrue(result)

        Tf = T.fmap(f)
        result = isinstance(Tf, Arrow(A, A))
        self.assertTrue(result)

        y = TA()
        result = T.fmap(f)(y)
        self.assertTrue(result == y)

        # type output equality
        self.assertTrue(TA == T(A))