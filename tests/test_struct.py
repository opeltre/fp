import pytest
import fp


class TestStruct:

    @fp.struct
    class Person:
        name: fp.Str
        number: fp.List(fp.Int)
        job: fp.Str = "Pizzaiolo"

    @fp.struct
    class Chiller:
        name: fp.Str

    @pytest.fixture(scope="class")
    def joe(self):
        return self.Person("joe", [0, 4, 3, 2])

    @pytest.fixture(scope="class")
    def jack(self):
        return self.Person("jack", [0, 1, 2, 3], "Plumber")

    def test_attributes_default(self, joe):
        assert joe.name == "joe"
        assert joe.number == [0, 4, 3, 2]
        assert joe.job == "Pizzaiolo"

    def test_attributes_no_default(self, jack):
        assert jack.name == "jack"
        assert jack.job == "Plumber"

    def test_field_getter(self):
        assert self.Person.name.src == self.Person
        assert self.Person.name.tgt == fp.Str

    def test_field_setter(self):
        assert self.Person.name.set.src == fp.Prod(fp.Str, self.Person)
        assert self.Person.name.set.tgt == self.Person

    def test_field_putter(self):
        assert self.Person.number.set.src == fp.Prod(fp.List(fp.Int), self.Person)
        assert self.Person.number.set.tgt == self.Person

    def test_get(self, joe):
        assert self.Person.job(joe) == "Pizzaiolo"

    def test_set(self, jack):
        jack2 = self.Person.job.set("Rock star")(jack)
        assert jack.job == "Plumber" and jack2.job == "Rock star"

    def test_put(self, jack):
        self.Person.job.put("Rock star")(jack)
        assert jack.job == "Rock star"

    def test_pull(self, jack):
        retired_jack = jack.pull(self.Chiller)
        assert isinstance(retired_jack, self.Chiller)
        assert retired_jack.name == "jack"
