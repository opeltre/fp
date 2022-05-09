from fp import Type, List, Arrow, Prod, Alg, AlgMeta


class Str(str, Type): 

    def __str__(self):
        return f"'{super().__str__()}'"


class Int(int, metaclass=AlgMeta):
    pass 

x = List(Str)(["abc", "d", "ef"])
y = List(Int)([0, 1, 2])

f = Arrow(Str, Int)(len)

@Arrow(Str, Int)
def length(s):
    return len(s)

@Arrow(Int, Str)
def bar(k):
    return "|" * k

@Arrow((Int, Int), Int)
def add (x, y):
    return x + y

Pair = Prod(Str, Str)
p = Pair("salut", "sava")

@Arrow((Str, Str), Int)
def g(x, y):
    return len(x) - len(y)

Person = Prod(Str, Int)
oli = Person("olivier", 29)
oli[0]
oli[1]