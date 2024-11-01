import fp
from fp.base import Int, Str
from fp.instances import State


class TestState:

    St = State(Str)

    length = St(Int)(lambda s: ("", len(s)))

    def test_new(self):
        StInt = self.St(Int)
        assert isinstance(StInt, fp.Type)

    def test_exec(self):
        assert self.length.exec("hello world") == ""

    def test_eval(self):
        assert self.length.eval("hello world") == 11

    def test_run_is_call(self):
        assert self.length.run("hello") == self.length("hello")

    def test_map(self):
        bar = fp.Hom(Int, Str)(lambda n: "|" * n)
        foobar = self.length.map(bar)
        assert foobar.eval("hello world") == Str("|||||||||||")
        assert foobar.exec("hello world") == Str("")

    def test_fmap(self):
        square = fp.Hom(Int, Int)(lambda n: n**2)
        length2 = self.St.fmap(square)(self.length)
        assert length2.eval("hello world") == 121

    def test_bind(self):

        @fp.Hom(Int, self.St(Int))
        def binary(n):
            q, r = divmod(n, 2)
            if r == 1:
                digit = self.St(Int)(lambda s: ("|" + s, q))
            else:
                digit = self.St(Int)(lambda s: ("." + s, q))
            # recursive bind
            return digit.bind(binary) if q > 0 else digit

        binlength = self.length.bind(binary)
        # 11 = 8 + . + 2 + 1
        assert binlength.exec("hello world") == "|.||"
