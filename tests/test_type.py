from fp.meta import Type


def test_decorator():

    @Type
    class Obj:
        x = 0

    assert isinstance(Obj, Type)
    assert Obj.x == 0


def test_metaclass():

    class Obj(metaclass=Type):
        x = 0

    assert isinstance(Obj, Type)
    assert Obj.x == 0
