import asyncio
import pytest
from time import time

import fp
from fp.meta import Type
from fp.cartesian import Hom
from fp.instances import Int, Str
from fp.instances.async_io import AsyncIO as IO
import fp.io.inputs


async def answer():
    return Int(42)


SLEEP_SECONDS = 1


class TestAsyncIO:

    io = IO(Int)(answer)

    def test_await(self):
        assert isinstance(self.io, IO(Int))
        assert hasattr(self.io, "__await__")

    def test_run(self):
        result = self.io.run()
        assert result == Int(42)

    def test_await(self):
        sleep = IO.sleep(SLEEP_SECONDS)

        @IO(Int)
        async def long_answer():
            await sleep
            return 42

        t0 = time()
        result = long_answer.run()
        t1 = time()
        assert result == 42
        assert abs(t1 - t0 - SLEEP_SECONDS) <= 0.05

    def test_fmap(self):
        add7 = Int.add(7)
        assert IO.fmap(add7)(self.io).run() == 49

    def test_map(self):
        mul3 = Int.mul(3)
        assert self.io.map(mul3).run() == 126

    def test_bind(self):

        @Hom(Int, IO(Int))
        def sub2(n):
            return IO.unit(n - 2)

        assert self.io.bind(sub2).run() == 40
        assert IO.bind(self.io, sub2).run() == 40

    def test_get(self, monkeypatch):
        monkeypatch.setattr(fp.io.inputs, "_input", lambda: "hello world!")
        assert IO.get().run() == "hello world!"

    def test_gets(self, monkeypatch):
        monkeypatch.setattr(fp.io.inputs, "_input", lambda: "hello world!")
        assert IO.gets(Str.len).run() == 12
