from fp.cartesian import Type, Hom, Prod
from fp.meta.method import Method, ClassMethod
from fp.meta import Var
from fp.base import Int


class Counter(metaclass=Type):

    def __new__(cls, n: int = 0):
        return object.__new__(cls)

    def __init__(self, n: int = 0):
        self.data = n

    @Method.annotate(lambda T: Hom(T, T))
    def inc(self):
        return self.__class__(self.data + 1)

    @Method
    def mult(self: Var("Counter"), n: Int) -> Var("Counter"):
        return self.__class__(self.data * n)

    @ClassMethod
    def init(cls: Var("Type"), n: Int) -> Var("Type"):
        return cls(n)

    @ClassMethod
    def init_empty(cls: Var("Type")) -> Var("Type"):
        return cls()


class TestMethod:

    def test_type_decorator(self):
        assert isinstance(Counter, Type)

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


class TestClassMethod:

    class Counter2(Counter):

        def __init__(self, n: int = 0):
            self.data = n * 2

    def test_decorator_signature(self):
        assert Counter.init.src == Int
        assert Counter.init.tgt == Counter

    def test_decorator_eval(self):
        ctr = Counter.init(3)
        assert isinstance(ctr, Counter)

    def test_decorator_child_class(self):
        ctr = self.Counter2.init(4)
        assert ctr.data == 8

    def test_decorator_unary(self):
        ctr = Counter.init_empty()
        assert ctr.data == 0
