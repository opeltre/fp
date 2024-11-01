from fp import *
from fp import utils
from fp.instances import State

# `State(Int, Str)` subclasses `Int -> (Int, Str)`


@State(Int, Str)
def barbaz(n):
    """Update an integer and return a string."""
    q, r = divmod(n, 2)
    if q == 0:
        return q, "|" if r else "*"
    return q, "|:" if r else "*:"


# The `State(Int)` monad binds `a -> State(Int, b)` functions


@Hom(Str, State(Int, Str))
def foobarbaz(acc):
    """Do `barbaz` while the accumulator says to continue."""
    # run with io.VERBOSITY = 1 for step logs
    utils.log(acc, v=1)
    if not len(acc) or acc[-1] != ":":
        # return accumulator
        return State(Int).unit(acc)
    else:
        # accumulate barbaz recursively
        accbarbaz = barbaz.map(Str.add(acc[:-1]))
        return accbarbaz >> foobarbaz


foo = foobarbaz(":")
foo.show()
foo(257).show()
foo(260).show()

from time import time, sleep


def foodo(n: int, dt: float):
    for i in range(n):
        t = time()
        k = int(t * 10_000_000) - int(t * 10) * 1_000_000
        print(foo(k))
        sleep(dt)


# foodo(20, .2)
