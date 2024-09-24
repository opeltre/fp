import fp
from fp import Type, Prod

def test_new(): 
    int_str = Prod(int, str)
    assert isinstance(int_str, fp.Type)

def test_init():
    pair = Prod(int, str)(3, "abc")
    assert type(pair) is Prod(int, str)

def test_proj():
    int_str = Prod(int, str)
    p0, p1 = int_str.proj(0), int_str.proj(1)
    pair = int_str(9, "cuzco")
    assert p0(pair) == 9
    assert p1(pair) == "cuzco"