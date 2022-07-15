import unittest

from fp.meta import TypeMeta, Arrow

A = TypeMeta("A", (int,), {})
B = TypeMeta("B", (str,), {})

foo = Arrow(B, A)(lambda y: len(y))
bar = Arrow(A, B)(lambda x: '|' * x)

@Arrow((A, A), A)
def power(x, y):
    return x ** y

class TestArrow(unittest.TestCase):

    def test_src_tgt(self):
        result = (bar.src, bar.tgt, foo.src, foo.tgt)
        expect = (A, B, B, A)
        self.assertEqual(expect, result)

    def test_matmul(self):
        foobar = foo @ bar
        barfoo = bar @ foo
        result = (foobar.src, foobar.tgt, barfoo.src, barfoo.tgt)
        expect = (A, A, B, B)
        self.assertEqual(expect, result)
    
    def test_call(self):
        x = A(18)
        y = B("Eilenberg Mac-Lane")
        self.assertEqual(x, foo(y))
        z = bar(18)
        self.assertTrue(isinstance(z, B))
        self.assertEqual(z, (bar @ foo)(y))

    def test_curry(self):
        """ Test curryfication """
        pow2 = power(2)
        result = type(power)
        expect = Arrow(A, A)
        self.assertTrue(expect, result)
        self.assertEqual(pow2(3), A(8))

    def test_untyped(self):
        add = Arrow((int, int), int)(int.__add__)
        self.assertEqual(add(2, 3), 5)


class TestAbstractArrow(unittest.TestCase):

    class Order(Arrow): 

        def __new__(cls, A, B, data=None): 
            
            class TAB(Arrow(A, B)):

                arity = 0

                def __init__(self, data=None):
                    super().__init__(lambda : None)
                    self.data = data

        @classmethod
        def name(cls, A, B):
            return f'{A} > {B}'

    def test_abstract_arrow(self):
        Order = self.__class__.Order
        ab = Order('a', 'b')


    
