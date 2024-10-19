"""Base test class for Tensor implementations."""

import pytest
from fp.tensors import Tensor, Numpy


class _TestTensor:

    T: type

    def test_constructor(self):
        x = self.T([0, 1, 2])
        assert isinstance(x, self.T)

    def test_iter_vector(self):
        tuple_x = (0, 1, 2)
        x = self.T(tuple_x)
        assert tuple(x) == tuple_x

    def test_add_operator(self):
        x = self.T((0, 1, 2))
        y = self.T((3, 2, 1))
        assert tuple(x + y) == (3, 3, 3)

    @pytest.mark.skip("__get__(obj) broken?")
    def test_add_bound(self):
        x = self.T((0, 1, 2))
        y = self.T((3, 2, 1))
        assert tuple(x.add(y)) == (3, 3, 3)

    def test_add_unbound(self):
        x = self.T((0, 1, 2))
        y = self.T((3, 2, 1))
        assert tuple(self.T.add(x, y)) == (3, 3, 3)

    def test_add_partial(self):
        x = self.T((0, 1, 2))
        y = self.T((3, 2, 1))
        add_x = self.T.add(x)
        assert (add_x.src, add_x.tgt) == (self.T, self.T)
        assert tuple(add_x(y)) == (3, 3, 3)


class TestTensor(_TestTensor):
    T = Tensor


class TestNumpy(_TestTensor):
    T = Numpy
