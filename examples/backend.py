from fp.instances import *
from fp.cartesian import *


import numpy 

from types import ModuleType
from typing import Callable


@struct
class API:
    name: Str
    Array: type = List(Float)

api = API("api")
np = API("numpy")

class StatefulStruct(Stateful):
    
    class _defaults_(Stateful._defaults_):
        ...

    def __new__(cls, S: type, s0 = None, dct=None):
        print("new Stateful", S)
        St = super().__new__(cls, S, s0)
        cls._post_new_(St, S, s0, dct)
        return St
    

    def _post_new_(St, S: type, s0 = None, dct=None):
        for field in St._state_:

            def get_field(key):

                # Use a StatefulField(Field) descriptor
                @property
                def getter(stateful):
                    print("> get field")
                    return getattr(stateful.state, key)

                getter.__get__(None, St)
                getter.__set_name__(key, St.Object)
                setattr(St.Object, key, getter)

            get_field(field)


@struct
class Interface:
    module : ModuleType
    Array : type
    asarray : Callable
    dtypes : List(Str)
    # aliases
    repeat : Str = "repeat"
    tile : Str = "tile"

@struct
class Lift:
    name: Str
    signature: Callable
    lift_args: type(...) | int | tuple = ...
    bind_arg: int = 0



Backend = StatefulStruct(API, api)
