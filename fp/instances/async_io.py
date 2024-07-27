from __future__ import annotations
import asyncio
import functools
from typing import Awaitable

from fp.meta import Type, Monad
from fp.cartesian import Type, Hom


class Coroutine(Hom.Object):
    """
    Base class for coroutines.
    """


class AsyncIO(Type, metaclass=Monad):
    """
    Asynchronous future, promised values.

    The awaitable type `AsyncIO(A)` represents asynchronous processes
    yielding an output value of type `A`. The output value can be
    awaited for with the `run` method.

        * `run : AsyncIO(A) -> A`
    """

    src = Type
    tgt = Type

    class Object(Monad._instance_):

        _type_: Type

        def __init__(self, pipe: Awaitable | tuple[Awaitable]):
            if hasattr(pipe, "__call__"):
                self._pipe = (pipe,)
            elif isinstance(pipe, tuple):
                self._pipe = pipe
            else:
                raise AttributeError(f"{pipe} is not callable and not a tuple")

        def __await__(self):
            f, *gs = self._pipe
            out = yield from f().__await__()
            for g in gs:
                out = yield from g(out).__await__()
            return out

        def run(self):
            return asyncio.run(self.__await__())

        def __str__(self):
            return " | ".join(str(f) for f in self._pipe)

        def __repr__(self):
            def repr_one(f):
                return f.__name__ if hasattr(f, "__name__") else str(f)

            return " | ".join(repr_one(f) for f in self._pipe)

    @classmethod
    def new(cls, A):
        IOA = super().new(cls, A)
        IOA.src = Type.Unit
        IOA.tgt = A
        return IOA

    @classmethod
    def unit(cls, x):
        async def return_x():
            return x

        return_x.__name__ = f"return {x}"
        return cls(type(x))(return_x)

    @classmethod
    def bind(cls, io_x, io_f):
        tgt = io_f.tgt
        return tgt((*io_x._pipe, io_f))

    @classmethod
    def sleep(cls, seconds: int | float) -> cls(Type.Unit):
        sleep_secs = functools.partial(asyncio.sleep, seconds)
        sleep_secs.__name__ = f"sleep {seconds}"
        return cls(Type.Unit)(sleep_secs)
