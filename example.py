from fp import Type, List, Arrow, Prod


class Str(str, Type): 

    def __str__(self):
        return f"'{super().__str__()}'"


class Int(int, Type): 

    def __add__(self, other):
        out = super().__add__(other)
        return self.__class__(other)
        
    
x = List(Str)(["abc", "d", "ef"])
y = List(Int)([0, 1, 2])

f = Arrow(Str, Int)(len)

Pair = Prod(Str, Str)
p = Pair("salut", "sava")

@Arrow(Str, Int)
def length(s):
    return len(s)
