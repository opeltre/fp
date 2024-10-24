from fp.meta import Var
from fp.instances import List, Int


def test_substitute():
    assert Var("A").substitute({"A": Int}) == Int


def test_substitute_nested():
    assert List("A").substitute({"A": Int}) == List(Int)


def test_match():
    assert List("A").match(List(List(Int)))["A"] == List(Int)
