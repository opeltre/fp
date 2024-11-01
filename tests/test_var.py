from fp.meta import Var
from fp.cartesian import Hom, Prod
from fp.base import List, Int, Str


def test_substitute():
    assert Var("A").substitute({"A": Int}) == Int


def test_substitute_nested():
    assert List("A").substitute({"A": Int}) == List(Int)


def test_substitute_hom():
    assert Hom("A", "A").substitute({"A": Int}) == Hom(Int, Int)


def test_substitute_prod():
    assert Prod(Int, Str, Int) == Prod(Var("A"), Var("B"), Var("A")).substitute(
        {"A": Int, "B": Str}
    )


def test_match():
    assert List("A").match(List(List(Int)))["A"] == List(Int)
