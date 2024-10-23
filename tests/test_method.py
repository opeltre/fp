from fp.cartesian import Type, Hom, Prod
from fp.cartesian.method import Method, method
from fp.meta import Var


class Counter(Type):
    _tail_ = None

    def __init__(self, n: int = 0):
        self.data = n

    @Method.annotate(lambda T: Hom(T, T))
    def inc(self):
        return self.__class__(self.data + 1)

    @method
    def mult(self: Var("Counter"), n: int) -> Var("Counter"):
        return self.__class__(self.data * n)


class TestMethod:

    @staticmethod
    def test_annotate_bound():
        counter = Counter()
        assert (counter.inc.src, counter.inc.tgt) == (Prod(), Counter)

    @staticmethod
    def test_annotate_unbound():
        assert Counter.inc.src, Counter.inc.tgt == (Counter, Counter)

    @staticmethod
    def test_decorator_bound():
        counter = Counter(1)
        counter.mult(2)

    @staticmethod
    def test_decorator_unbound():
        assert len(Counter.mult.src) == 2
