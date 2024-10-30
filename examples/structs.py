from fp.base import *
from fp.cartesian import *
from fp import utils

from math import pi, log10

"""
The `struct` decorator returns a new instance of `Type` 
with dataclass-like behaviour.
"""


@Hom(Int, List(Int))
def phone(n):
    i = int(log10(pi * n)) + 1
    return str(pi * n).replace(".", "0")[i : i + 10]


@struct
class Person:
    name: Str
    phone: List(Int) = []


jack = Person("Jack", List.range(10)).show()
lucy = Person("Lucy", "0234723965").show()

"""
Struct types can be nested and have default values.
"""


@struct
class Family:
    parents: List(Person)
    children: List(Person) = []
    hometown: Str = "Milwaukee"


myfamily = Family([jack, lucy], [Person("I")])
myfamily.show()

"""
Struct instances are mutable by default. 
They however use `__slots__`, which means that trying to assign 
a value to a non-existing key will raise an `AttributeError`. 
"""
try:
    jack.age = 45
except Exception as e:
    print(jack.name, "has no age")

"""
Structs also support inheritance. 
Child classes always have larger sets of keys, and are 
mapped to the parent class by forgetting external keys.
"""


@struct
class Biker(Person):
    frame: Int
    wheels: Str = "Mavic"
    role: Str = "climber"


joe = Biker("Joe", frame=21, role="sprinter")
jane = Biker("Jane", frame=18, phone=phone(1))

"""
The `Struct(keys, values)` bifunctor is contravariant in its 
left `keys` argument. 
"""

utils.cast(joe, Person) is joe

"""
This means that subclasses of any `Struct` type can be 
used in place of it in typed lists, tuples, other 
struct fields, etc. To explicitly create a superclass 
copy instance from the fields of a child class, call 

    >>> child.pull(parent)
"""
# joe.pull(Person) is joe
# print(type(joe.pull(Person)))

cousins = Family(
    parents=[joe, jane],
    children=[Person("Will", phone(2)), Person("Mary", phone(3))],
    hometown="Worcester",
)

cousins.show()
