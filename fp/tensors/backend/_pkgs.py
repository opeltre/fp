import pkg_resources
import os

import numpy as np

# --- Get available backends ---

pkgs = [p.project_name for p in pkg_resources.working_set]

has_jax = "jax" in pkgs
has_torch = "torch" in pkgs

del pkgs

# --- Export references ---

if has_jax:
    import jax
else:
    jax = False

if has_torch:
    import torch
else:
    torch = False

jnp = has_jax and jax.numpy

