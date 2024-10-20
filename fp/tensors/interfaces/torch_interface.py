from fp.instances import struct
from .interface import Interface, DtypeTable, INTERFACES


@struct
class DtypeTableTorch(DtypeTable):
    # aliases
    int32: str = "int"
    int64: str = "long"
    float32: str = "float"
    float64: str = "double"
    complex64: str = "cfloat"
    complex128: str = "cdouble"


try:
    import torch

    HAS_TORCH = True

    @struct
    class TorchInterface(Interface):
        module = torch
        # array class and constructor
        Array = torch.Tensor
        asarray = torch.as_tensor
        # dtypes : torch.Tensor.<alias>(x)
        dtypes = DtypeTableTorch()
        dtypes_bind = "Array"
        # repeats
        repeat = "repeat_interleave"
        tile = "repeat"

    INTERFACES["torch"] = TorchInterface()

except ModuleNotFoundError:
    torch = None
    HAS_TORCH = False
