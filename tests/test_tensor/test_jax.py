import pytest

from _test_tensor import _TestTensor
from fp.tensors import Jax


class TestJax(_TestTensor):
    T = Jax

    @pytest.mark.skip("TODO: Jax enable int64")
    def test_int64(self): ...

    @pytest.mark.skip("TODO: Jax enable float64")
    def test_float64(self): ...
