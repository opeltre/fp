from fp import *
from fp import io

@State(Int, Str)
def barbaz(n):
    """Update an integer and return a string."""
    q, r = divmod(n, 2)
    if q == 0:
        return q, "|" if r else "*"
    return q, "|<" if r else "*<"

@Hom(Str, State(Int, Str))
def foobarbaz(acc):
    """Do `barbaz` while the accumulator says to continue."""
    io.log(acc, v=1)
    if len(acc) and acc[-1] == "<":
        # accumulate output
        accbarbaz = barbaz.map(Str.add(acc[:-1]))
        # bind foobarbaz
        return accbarbaz >> foobarbaz
    else: 
        # return accumulator
        return State(Int).unit(acc)

foobarbaz("acc <").show()
print("foobarbaz < 257")
foobarbaz("<").run(257).show()
print("foobarbaz < 260")
foobarbaz("<").run(260).show()

@Hom(Int, Prod(Int, Str) ** (Int, Str))
def put(n):
    put_n = lambda i, out: (n, Str.add(out, "_<"))
    put_n.__name__ = "resume " + str(n)
    return put_n

@Hom(List(Int), State(Int, Str))
def foo(ns):
    # stop
    if not len(ns):
        return State(Int).unit(Str(""))
    # resume
    *ms, n = ns
    return foo(ms).then(put(n)).bind(foobarbaz)
