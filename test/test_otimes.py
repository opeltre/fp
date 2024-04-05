import unittest
import torch

from fp import Tens, Linear, Otimes

E, F = Tens([3]), Tens([2, 3])
A, B = Tens([4]), Tens([6])

class TestOtimes(unittest.TestCase):

    def test_obj(self):
        """ Tensor product of linear spaces """
        result = Otimes(E, F)
        expect = Tens([3, 2, 3])
        self.assertTrue(issubclass(result, expect))

    def test_pure(self):
        """ Tensor product of two vectors, a.k.a. pure tensor """
        x = E.range() + 1
        y = A.range() + 1
        xy = Otimes(E, A).pure(x, y)
        result = xy.data
        expect = torch.tensor([[1, 2, 3, 4],
                               [2, 4, 6, 8],
                               [3, 6, 9, 12]])
        self.assertTrue((result == expect).prod())

    def test_fmap_dense(self):
        """ Tensor product of two dense operators """
        f = Linear(E, F).randn()
        g = Linear(A, B).randn()
        fg = Otimes.fmap(f, g)
        x = E.randn()
        y = A.randn()
        result = fg(x | y)
        expect = f(x) | g(y)
        self.assertTrue((result.data - expect.data).norm() < 1e-5)

    def test_fmap_sparse(self):
        """ Tensor product of two sparse operators """
        f = Linear(E, F).randn()
        g = Linear(A, B).randn()
        f.data, g.data = f.data.to_sparse(), g.data.to_sparse()
        fg = Otimes.fmap(f, g)
        x = E.randn()
        y = A.randn()
        result = fg(x | y)
        expect = f(x) | g(y)
        self.assertTrue((result.data - expect.data).norm() < 1e-5)