from fp.cartesian import Hom, Prod
from fp.cartesian.method import Method


class Counter:

    def __init__(self, n: int = 0):
        self.data = n

    @Method.annotate(lambda T: Hom(T, T))
    def inc(self):
        return self.__class__(self, self.data + 1)


class TestMethod:

    @staticmethod
    def test_annotate_bound():
        counter = Counter()
        assert (counter.inc.src, counter.inc.tgt) == (Prod(), Counter)

    @staticmethod
    def test_annotate_unbound():
        assert Counter.inc.src, Counter.inc.tgt == (Counter, Counter)
