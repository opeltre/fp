import fp
from fp.base import Str
from fp.instances import Stateful


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

    def test_use_context(self):
        get = self.M.get
        with self.M.use("toto"):
            s1 = get.state
        assert s1 == "toto"

    def test_map(self):
        length = self.M.get.map(Str.len)
        assert length.value == 3

    def test_map_use(self):
        length = self.M.get.map(Str.len)
        with self.M.use(""):
            assert length.value == 0

    def test_mock(self):
        mock = self.M.get.mock()
        assert mock.__len__() == 3

    def test_mock_use(self):
        mock = self.M.get.mock()
        with self.M.use(""):
            assert mock.__len__() == 0
