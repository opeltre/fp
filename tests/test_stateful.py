import fp
from fp.instances import Stateful, Str


class TestStateful:

    M = Stateful(Str, "0.0")
    s0 = "0.0"

    def test_is_monad(self):
        assert isinstance(self.M, fp.meta.Monad)

    def test_new(self):
        MInt = self.M(fp.Int)
        assert isinstance(MInt, fp.Type)
        assert type(MInt) is self.M

    def test_initial_state(self):
        s0 = self.M.get.state
        assert s0 == self.s0
