import unittest
import torch

from fp import Tens, Arrow

Tx = Tens([3, 2])
Ty = Tens([3])

def assertClose(test, x, y):
    return test.assertTrue((x.data - y.data).norm() < 1e-7)

class TestTens(unittest.TestCase):
    
    def test_add_type(self):
        result = type(Tx.add)
        expect = Arrow((Tx, Tx), Tx)
        self.assertEqual(expect, result)
    
    def test_add(self):
        x1, x2 = Tx.ones(), Tx([[2, 2]]*3)
        expect = Tx([[3, 3]]*3)
        for result in [Tx.add(x1, x2), x1 + x2]:
            assertClose(self, expect, result)
            self.assertTrue(isinstance(result, Tx))

    def test_cast(self):
        result = Tx(1)
        expect = Tx.ones()
        assertClose(self, expect, result)
        result = Ty.ones() * 3
        expect = Ty([3, 3, 3])
        assertClose(self, expect, result)

    def test_add_curry(self):
        y = Ty.randn()
        add_y = Ty.add(y)
        result = type(add_y)
        expect = Arrow(Ty, Ty)
        self.assertEqual(expect, result)
        self.assertTrue(isinstance(add_y(y), Ty))