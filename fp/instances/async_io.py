from __future__ import annotations
import asyncio
import functools
from typing import Awaitable, TypeAlias

from fp.meta import Type, Monad
from fp.cartesian import Type, Hom
from fp.instances import Str
import fp.io as io


async def _sleep(seconds: int | float) -> Type.Unit:
    """Sleep and return ()."""
    await asyncio.sleep(seconds)
    return Type.Unit()


class AsyncIO(Type, metaclass=Monad):
    """
    Asynchronous promises for type values.

    The awaitable type `AsyncIO(A)` represents asynchronous processes
    yielding an output value of type `A`. The output value can be
    awaited for with the `run` method.

        * `run : AsyncIO(A) -> A`

    Example
    -------
        >>> from fp.instances import AsyncIO as IO
        >>> @AsyncIO(Int)
        ... async def answer():
        ...     await AsyncIO.sleep(1)
        ...     return 42
        ...
        >>> answer.map(Int.add(5)).run()
        >>> 47
    """

    src = Type
    tgt = Type

    Get: TypeAlias = Str

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

    # --- Monad methods ---

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

    # --- IO methods ---

    @classmethod
    def get(cls) -> cls(Str):

        @cls(Str)
        async def getLine():
            return Str(io.inputs._input())

        return getLine

    @classmethod
    def gets(cls, f: Callable, tgt: type | None = None) -> cls.Object:

        if tgt is None:
            tgt = f.tgt
        else:
            f = Hom(Str, tgt)(f)

        async def gets_f():
            return io.cast(f(io.inputs._input()), tgt)

        gets_f.__name__ = f"gets {f.__name__}"
        return cls(tgt)(gets_f)

    @classmethod
    def sleep(cls, seconds: int | float) -> cls(Type.Unit):
        sleep_secs = functools.partial(_sleep, seconds)
        sleep_secs.__name__ = f"sleep {seconds}"
        return cls(Type.Unit)(sleep_secs)
