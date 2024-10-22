import pytest
from fp.tensors import Tens


class TestTens:

    T = Tens

    def test_new(self):
        T23 = self.T((2, 3))
        assert isinstance(T23, self.T)
        assert T23.shape == (2, 3)
        assert hasattr(T23, "domain")

    def test_zeros(self):
        zeros = self.T((2, 3)).zeros()
        assert zeros.shape == (2, 3)

    def test_ones(self):
        ones = self.T((4,)).ones()
        assert ones.shape == (4,)

    def test_range(self):
        idx = self.T((2, 3)).range()
        flattened = tuple(int(i) for i in idx.data.flatten())
        assert flattened == (0, 1, 2, 3, 4, 5)

    @pytest.mark.skip("TODO: torch specific")
    def test_randn(self):
        gauss = self.T((2, 3)).randn()
        assert gauss.shape == (2, 3)

    @pytest.mark.skip("TODO: fix this, use outer")
    def test_otimes(self):
        R2 = self.T((2,))
        lhs = R2((1, -1))
        rhs = R2((1, -1))
        expect = (1, -1, -1, 1)
        result = lhs.otimes(rhs)
        assert expect == tuple(int(i) for i in result.data.flatten())
