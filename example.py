from fp import *

x = List(str)(["abc", "d", "ef"])
y = List(int)([0., 1., 2.])

f = Arrow(str, int)(len)

@Arrow(str, int)
def length(s):
    return len(s)
