from fp.meta import Type
from .arrow import Arrow
from .hom import Hom
from .prod import Prod
from .num import Eq, Bool
from .num import Operad, Monoid, Ring, Alg
from .num import Int, Float, Str
from .num import Str
from .list import List

from .wrap import Wrap
from .either import Either

__all__ = [
    "Prod",
    "Arrow",
    "Hom",
    "Monoid",
    "Ring",
    "Alg",
    "Bool",
    "Int", 
    "Float",
    "List",
    "Str",
    "Wrap",
    "Either",
]
