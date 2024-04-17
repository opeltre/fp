import torch
from fp.instances import Type, Hom, Wrap, Alg, Ring

signature = lambda n : lambda A: Hom(tuple([A] * n), A)

class WrapRing(Wrap, Ring):

    _lifted_methods_ = [
        ("__add__", signature(2) , ...),
        ("__sub__", signature(2), ...),
        ("__mul__", signature(2), ...),
        ("__truediv__", signature(2), ...),
        ("__neg__", signature(1), ...),
    ]

    @classmethod
    def new(cls, A):
        Wrap_A = super().new(A)
        # torch.tensor is the correct torch.Tensor constructor
        if A == torch.Tensor:
            Wrap_A.cast_data = torch.as_tensor
            # torch.tensor casts
            for T in ["float", "cfloat", "long", "double"]:
                method = lambda x: x.__class__(getattr(A, T)(x.data))
                setattr(Wrap_A, T, method)
        return Wrap_A
