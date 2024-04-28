from fp.instances import *
from fp.cartesian import *
from fp import io

"""
The `struct` decorator returns a new instance of `Type` 
with dataclass-like behaviour.
"""
@struct
class Person:
    name: Str
    phone: List(Int) = []

jack = Person("Jack", List.range(10)).show()
lucy = Person("Lucy").show()

"""
Structs types can be nested and have default values.
"""
@struct 
class Family:
    parents: List(Person)
    children: List(Person) = []
    hometown: Str = "Milwaukee"

myfamily = Family([jack, lucy])
myfamily.show()

"""
Structs also support inheritance. 
Child classes always have larger sets of keys, and are 
mappted to the parent class by forgetting external keys.
"""

@struct
class Biker(Person):
    frame: Int 
    wheels: Str = "Mavic"
    role: Str = "climber"

joe = Biker("Joe", frame=21, role="sprinter").show()
jane = Biker("Jane", frame=18).show()

io.cast(joe, Person) is joe

"""
The `Struct(keys, values)` bifunctor is contravariant in its 
left `keys` argument. 
"""
