from __future__ import annotations
import asyncio
import functools
from typing import Awaitable, Iterable, TypeAlias

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

    class Object(Monad.TopType):

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

        async def __call__(self):
            out = await self
            return out

        def __str__(self):
            return " | ".join(str(f) for f in self._pipe)

        def __repr__(self):
            def repr_one(f):
                return f.__name__ if hasattr(f, "__name__") else str(f)

            return " | ".join(repr_one(f) for f in self._pipe)

    @classmethod
    def new(cls, A):
        IOA = super().new(A)
        IOA.src = Type.Unit
        IOA.tgt = A
        IOA._type_ = A
        return IOA

    # --- Monad methods ---

    @classmethod
    def unit(cls, x) -> cls.Object:

        async def return_x():
            return x

        return_x.__name__ = f"return {x}"
        return cls(type(x))(return_x)

    @classmethod
    def bind(cls, io, io_fn):
        tgt = io_fn.tgt
        return tgt((*io._pipe, io_fn))

    # --- IO methods ---

    @classmethod
    def get(cls) -> cls(Str):

        @cls(Str)
        async def getLine():
            return Str(io.inputs._input())

        return getLine

    @classmethod
    def wait(
        cls, ios: Iterable[cls.Object], timeout=None, return_when="ALL_COMPLETED"
    ) -> cls.Object:
        """Wait for asynchronous processes to execute."""
        tgt = Type.Prod(*(io._type_ | None for io in ios))

        @cls(tgt)
        async def wait():
            tasks = []
            for io in ios:
                tasks.append(asyncio.create_task(io()))

            done, pending = await asyncio.wait(
                tasks,
                timeout=timeout,
                return_when=return_when,
            )
            for task in pending:
                task.cancel()

            out = []
            for task in tasks:
                if task.done():
                    val = task.result()
                    out.append(val)
                else:
                    out.append(None)
            return out

        return wait

    @classmethod
    def clear(cls, n: int) -> cls.Object:

        @cls(Type.Unit).named(f"clear {n}")
        async def clear_n():
            for i in range(n):
                print("\033[F\033[K")

        return clear_n

    @classmethod
    def gets(cls, f: Callable, tgt: type | None = None) -> cls.Object:

        if tgt is None:
            tgt = f.tgt
        else:
            f = Hom(Str, tgt)(f)

        async def gets_f():
            string = await cls.get()
            return f(string)

        gets_f.__name__ = f"gets {f.__name__}"
        return cls(tgt)(gets_f)

    @classmethod
    def sleep(cls, seconds: int | float) -> cls(Type.Unit):
        sleep_secs = functools.partial(_sleep, seconds)
        sleep_secs.__name__ = f"sleep {seconds}"
        return cls(Type.Unit)(sleep_secs)
