from fp.tensors import Tens


class TestTens:

    T = Tens

    def test_new(self):
        T1 = self.T((2, 3))
        assert isinstance(T1, self.T)
        assert T1.shape == (2, 3)
        assert hasattr(T1, "domain")

    def test_zeros(self):
        zeros1 = self.T((2, 3)).zeros()
        assert zeros1.shape == (2, 3)

    def test_range(self):
        idx1 = self.T((2, 3)).range()
        flattened = tuple(int(i) for i in idx1.data.flatten())
        assert flattened == (0, 1, 2, 3, 4, 5)
