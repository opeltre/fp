from fp.instances import struct
from .interface import Interface, INTERFACES
from .numpy import NumpyInterface

try:
    import torch

    HAS_TORCH = True

    @struct
    class TorchInterface(Interface):

        module = torch

        Array = torch.Tensor
        asarray = torch.as_tensor

        # dtypes
        dtypes = [
            "float",
            "double",
            "int",
            "long",
            "cfloat",
        ]

        repeat = "repeat_interleave"
        tile = "repeat"

    INTERFACES["torch"] = TorchInterface()

except ModuleNotFoundError:
    torch = None
    HAS_TORCH = False

torch_interface = TorchInterface() if HAS_TORCH else NumpyInterface()
