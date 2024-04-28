from fp.meta import Type
from .either import Either
from .prod import Prod
from .arrow import Arrow
from .hom import Hom
# make `Type` a cartesian category here 
Type.Sum = Either
Type.Prod = Prod
Type.Hom = Hom

Type.Unit = Prod.Unit
Type.Zero = Either.Unit

__all__ = [
    "Type", 
    "Hom",
    "Prod",
    "Either",
    "Arrow",
]
