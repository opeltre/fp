import fp.io as io
import fp.utils as utils
import fp.meta as meta
import fp.cartesian as cartesian
from fp.cartesian import *
import fp.instances as instances
from fp.instances import *

__all__ = cartesian.__all__ + instances.__all__ 

io.document(cartesian)
io.document(instances)
