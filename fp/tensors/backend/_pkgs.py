import os

import numpy as np

try:
    import jax

    has_jax = True
except ModuleNotFoundError:
    jax = None
    has_jax = False

try:
    import torch

    has_torch = True
except ModuleNotFoundError:
    torch = None
    has_torch = False

jnp = None if jax is None else jax.numpy
