import fp.utils as utils
import fp.meta as meta
import fp.cartesian as cartesian
import fp.base as base
import fp.instances as instances

from fp.cartesian import *
from fp.base import *

__all__ = cartesian.__all__ + base.__all__

utils.document(base)
utils.document(cartesian)
utils.document(instances)
