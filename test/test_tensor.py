import unittest
import torch

from fp import Tensor
from fp.meta import Arrow

x = Tensor(torch.ones([3]))
y = Tensor(2 * torch.ones([3]))

def assertClose(test, x, y):
    return test.assertTrue((x.data - y.data).norm() < 1e-7)

class TestTensor(unittest.TestCase):
    
    def test_add_type(self):
        result = type(Tensor.add)
        expect = Arrow((Tensor, Tensor), Tensor)
        self.assertEqual(expect, result)
    
    def test_add(self):
        expect = Tensor(torch.tensor([3., 3., 3.]))
        for result in [Tensor.add(x, y), x + y]:
            assertClose(self, expect, result)
            self.assertTrue(isinstance(result, Tensor))

    def test_cast(self):
        result = Tensor(1).data
        expect = torch.ones([])
        self.assertTrue((expect - result) == 0)

    def test_add_curry(self):
        add_x = Tensor.add(x)
        result = type(add_x)
        expect = Arrow(Tensor, Tensor)
        self.assertEqual(expect, result)
        assertClose(self, add_x(x), y)

    