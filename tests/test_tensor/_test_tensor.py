"""Base test class for Tensor implementations."""

import pytest


class _TestTensor:

    T: type

    def test_constructor(self):
        x = self.T([0, 1, 2])
        assert isinstance(x, self.T)

    def test_iter_vector(self):
        tuple_x = (0, 1, 2)
        x = self.T(tuple_x)
        assert tuple(x) == tuple_x

    def test_flatten_unbound(self):
        x = self.T(((0, 1), (2, 3)))
        x_flat = self.T.flatten(x)
        assert tuple(x_flat) == (0, 1, 2, 3)

    def test_flatten_bound(self):
        x = self.T(((0, 1), (2, 3)))
        x_flat = x.flatten()
        assert tuple(x_flat) == (0, 1, 2, 3)

    def test_neg(self):
        x = self.T((-1.0, 0.0, 1.0))
        x = -x
        assert tuple(i for i in x.data) == (1.0, 0.0, -1.0)

    def test_add_operator(self):
        x = self.T((0, 1, 2))
        y = self.T((3, 2, 1))
        assert tuple(x + y) == (3, 3, 3)

    @pytest.mark.skip("TODO with Lifts and Methods?")
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

    def test_int32(self):
        x = self.T((0.0, 1.0, 2.0))
        y = self.T.int32(x)
        dtype = str(y.data.dtype)
        assert dtype.find("int") >= 0

    def test_int64(self):
        x = self.T((0, 1, 2))
        y = self.T.int64(x)
        dtype = str(y.data.dtype)
        assert dtype.find("int64") >= 0 or dtype.find("long") >= 0

    def test_float32(self):
        x = self.T((0, 1, 2))
        y = self.T.float32(x)
        dtype = str(y.data.dtype)
        assert dtype.find("float32") >= 0 or dtype.find("double") >= 0

    def test_float64(self):
        x = self.T((0, 1, 2))
        y = self.T.float64(x)
        dtype = str(y.data.dtype)
        assert dtype.find("float64") >= 0 or dtype.find("double") >= 0

    def test_complex64(self):
        x = self.T((0, 1, 2))
        y = self.T.complex64(x)
        dtype = str(y.data.dtype)
        assert dtype.find("complex64") >= 0 or dtype.find("cfloat") >= 0
