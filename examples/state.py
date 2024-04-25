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

class MyState(Stateful):
    _state_ = Str
    _initial_ = "Hello World!" 
