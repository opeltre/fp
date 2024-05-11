from fp import *
from fp.meta import *

bar = Hom(Int, Str)(lambda n: "|" * n)
foo = Hom(Str, Int)(len)

bar.shows("bar"), foo.shows("foo")

#--- Stateful string monad ---

St = State(Str)
print(repr(St))

Foo = State.gets(foo).show()
Bar = State.puts(bar).show()

FooBar = State.gets(foo) >> State.puts(bar)
FooBar.show()

print("\n>>> FooBar.run('abcd')")
FooBar.run("abcd").show()

print("""
>>> with FooBar.use("some initial state"):
...     FooBar.run()""")

with FooBar.use("some initial state"):
    FooBar.run().show()

print("\n")

#--- Monad subclasses ---

class MyString(Stateful(Str, "Hello World!")):
    ...

@Hom((Int, Str), Prod(Str, Int))
def baz(n, s):
    """
    Stateful string updates indexed by integers.
    """
    print(repr(s))
    if n >= len(s):
        return (s, -1)
    if s[n] == ' ':
        return (s, -n)
    s = s[:n] + '*' + s[n+1:]
    return (s, n + 1)

@Hom(Int, MyString(Int))
def loopbaz(n):
    """
    Do `baz` while value is not negative.
    """
    if n < 0:
        return MyString.unit(n)
    return MyString(Int)(baz(n)).bind(loopbaz)

resume = (Int.add(1) @ Int.neg).shows("resume")

@Hom(Int, MyString(Int))
def repeatbaz(n):
    """
    Resume and repeat `loop baz` exactly n times.
    """
    if n == 1:
        return loopbaz(0)
    elif n > 1:
        return repeatbaz(n - 1).map(resume).bind(loopbaz)

loopbaz.show()
loopbaz(0).value.show()
loopbaz(8).value.show()

#--- state context manager

with MyString.use("Foo Bar Baz"):
    repeatbaz(2).show()
    repeatbaz(2).value.show()
