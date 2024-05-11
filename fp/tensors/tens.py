import torch

from .backend.wrap_alg import WrapRing
from .tensor import Tensor, Backend
from .typed_tensor import TypedTensor
from .shape import Torus

from fp.meta import HomFunctor, Functor, NFunctor
from fp.cartesian import Type, Hom
from fp.instances import Ring
import fp.io as io

class Tens(Backend, Ring, metaclass=Functor):
    """
    Typed tensor spaces.

    The `Tens` functor maps shapes to their associated tensor type.

    **Example:**
    .. code:: 

        >>> E = Tens((3, 2))
        >>> E.range()
        Tens 3x2 : [[ 0,  1],
                    [ 2,  3],
                    [ 4,  5]]
    """

    @classmethod
    def new(cls, A):
        class Tens_A:

            shape = A
            domain = Torus(A)


        name = cls._get_name_(A)
        Tens_A.__name__ = name
        bases = (Tens_A, TypedTensor,)
        dct = dict(Tens_A.__dict__)
        dct["shape"] = tuple(A)
        dct["domain"] = Torus(A)
        TA = Ring.__new__(cls, name, bases, dct)
        io.log(("Tens new", TA, type(TA), type(TA) is cls), v=1)
        return TA
     
    def _post_new_(Tens_A, A):
        Backend._post_new_(Tens_A, Tensor._backend_)
        Ring.__init__(Tens_A, Tens_A.__name__) 
        cls = Tens_A.__class__
        io.log((cls, "_post_new_", Tens_A, A), v=1)

    def __init__(cls, A, *xs, **ks):
        ...

    @classmethod
    def _get_name_(cls, shape):
        return f'Tens {"x".join(str(n) for n in shape)}'

    @classmethod
    def fmap(cls, f):
        pass

    @classmethod
    def cofmap(cls, f, batch=True):
        ns, ms = f.src.n, f.tgt.n
        g = f.tgt.index @ f @ f.src.coords
        i = torch.arange(f.src.size)
        j = g(i) if batch else [g(ik) for ik in i]
        ij = torch.stack([i.data, j.data])
        mat = Tensor.sparse([g.src.size, g.tgt.size], ij)
        return Linear(ms, ns)(mat)

    def __str__(TA):
        return TA.__name__

    def __repr__(TA):
        return TA.__name__


class Linear(Hom, Tens, metaclass=HomFunctor):
    """
    Linear maps types, containing dense or sparse matrices.

    The homtype `Linear(A, B)` represents the category structure
    on linear spaces obtained by the `Tens` constructor.

    The arguments `A` and `B` can either be given as tensor shapes
    or as associated tensor types e.g.
        
    .. code::

        A, B = Tens((2, 3)), Tens((4))
        assert Linear(A, B) == Linear((2, 3), (4))

    Linear map instances inherit from the Hom class, overriding
    composition and application by matrix-matrix and matrix-vector
    products respectively.
    """

    class Object:
        
        def __new__(cls, matrix, name=None):
            self = super().__new__(cls, matrix, name)
            return self

        def __init__(self, matrix, name=None):
            cls = self.__class__
            # Tens([B, A]) attributes
            mat = matrix.data if isinstance(matrix, Tensor) else matrix
            if mat.is_sparse:
                mat = mat.coalesce()
            self.data = mat

            # Hom(Tens([A]), Tens([B])) attributes
            A, B = ("x".join(str(n) for n in C) for C in self._tail_)
            if mat.is_sparse:
                nnz = mat.indices().shape[-1]
                self.__name__ = f"sparse {B}<{A} (nnz={nnz})"
            else:
                self.__name__ = f"dense {B}<{A}"

        @classmethod
        def matvec(cls, mat, x):
            """Matrix vector product."""
            if isinstance(x, (Tensor, torch.Tensor)):
                sx = list(x.shape)
                src = list(cls.src.shape)
                M, X = mat.data, x.data
                # cast dtype
                if torch.is_complex(M) and not torch.is_complex(X):
                    X = X.complex()
                if M.is_floating_point() and not X.is_floating_point():
                    X = X.float()
                # apply to 1d vector
                if sx == [cls.src.domain.size]:
                    return M @ X
                # apply to tensor
                elif sx == src:
                    return M @ X.view([-1])
                # apply to last dimensions of tensor
                elif sx[-len(src) :] == src:
                    n1 = cls.src.domain.size
                    xT = X.view([-1, n1]).T
                    return (M @ xT).T
                raise TypeError(f"Did not find a caller for input {x.shape}")

        def __mul__(self, other):
            if isinstance(other, (int, float)):
                return self.__class__(
                    self.data * other, name=f"{other} * {self.__name__}"
                )
            if isinstance(other, torch.Tensor) and other.numel() == 1:
                return self.__class__(
                    self.data * other, name=f"{other} * {self.__name__}"
                )
            return super().__mul__(other)

        def __rmul__(self, other):
            if isinstance(other, (int, float)):
                return self.__mul__(other)
            if isinstance(other, torch.Tensor) and other.numel() == 1:
                return self.__mul__(other)
            return super().__rmul__(other)

        def t(self):
            """Adjoint operator in Linear(B, A)."""
            A, B = self._tail_
            return Linear(B, A)(self.data.t())

        def __repr__(self):
            return self.__name__
    
    # --- Type creation 

    @classmethod
    def new(cls, A, B):
        src, tgt = Tens(A), Tens(B)
        bases = cls.Object, Tens((*B, *A)), Hom(src, tgt)
        name = cls._get_name_(A, B)
        LAB = Ring.__new__(cls, name, bases, {})
        Ring.__init__(LAB, name, bases, {})
        return LAB
    
    @classmethod
    def _get_name_(cls, A, B):
        name_one = lambda C: "x".join(str(n) for n in C)
        A, B = name_one(A), name_one(B)
        return f"Linear {A} {B}"

    @classmethod
    def _pre_new_(cls, A, B):
        def parse_one(C):
            if isinstance(C, tuple):
                return C
            if isinstance(C, int):
                return (C,)
            if isinstance(C, Ring):
                return C.shape
            elif isinstance(C, list):
                return tuple(C)
        return parse_one(A), parse_one(B)
    
    def _post_new_(LinAB, A, B, *xs):
        msg = (str(m) for m in (LinAB.__name__, "_post_new_", A, B, *xs))
        io.log(" ".join(msg), v=1)
        cls = LinAB.__class__
        Backend._post_new_(LinAB, LinAB._backend_)
    
    # --- Class methods 
    
    @classmethod
    def compose(cls, f, *gs):
        if not len(gs):
            return f
        g = gs[0]
        if len(gs) > 1:
            return cls.compose(cls.compose(f, g), *gs[1:])
        """Composition of matrices."""
        if f.data.is_sparse and g.data.is_sparse:
            data = torch.sparse.mm(g.data, f.data)
        else:
            data = g.data @ f.data
        gf = cls(f.src, g.tgt)(data)
        return gf

    @classmethod
    def eval(cls, x, f):
        return f @ x
    
    @classmethod
    def source_type(cls, f, xs):
        assert (len(xs)) == 1
        x = xs[0]
        s_x = tuple(x.shape)
        s_in = tuple(f.src.domain.shape)
        if s_x == s_in:
            return f.src
        elif s_x[-len(s_in) :] == s_in:
            return Tens(s_x)

    @classmethod
    def target_type(cls, f, xs):
        assert (len(xs)) == 1
        x = xs[0]
        s_x = tuple(x.shape)
        s_in = tuple(f.src.domain.shape)
        s_out = tuple(f.tgt.domain.shape)
        if s_x == s_in:
            return f.tgt
        elif s_x[-len(s_in) :] == s_in:
            return Tens((*s_x[: -len(s_in)], *s_out))

    @classmethod
    def otimes(cls, f, g):
        """Tensor product of matrices."""
        # input matrices
        if f.data.is_sparse and g.data.is_sparse:
            F, G = f.data, g.data
        if f.data.is_sparse and not g.data.is_sparse:
            F, G = f.data, g.data.to_sparse()
        elif not f.data.is_sparse and g.data.is_sparse:
            F, G = f.data.to_sparse(), g.data
        else:
            F, G = f.data, g.data
        # sparse tensor product
        if F.is_sparse and G.is_sparse:
            # input sparse matrices
            F, G = f.data.coalesce(), g.data.coalesce()
            Ng, Mg = G.shape
            Nf, Mf = F.shape
            # tensor product on indices
            ij, ab = F.indices(), G.indices()
            Vf, Vg = F.values(), G.values()
            IJ = ij.repeat_interleave(ab.shape[1], 1)
            AB = ab.repeat(1, ij.shape[1])
            XY = torch.tensor([Ng, Mg])[:, None] * IJ + AB
            val = Vf.repeat_interleave(Vg.shape[0], 0) * Vg.repeat(Vf.shape[0])
            # output sparse matrix
            shape = [Nf * Ng, Mf * Mg]
            data = torch.sparse_coo_tensor(XY, val, shape, device=F.device)
            return data
        # dense tensor product
        raise Exception("Dense tensor product of operators not implemented")


class Otimes(metaclass=NFunctor):
    """
    Tensor product of linear spaces.
    """

    start_dim = 0

    def __new__(cls, Tens_A, Tens_B):
        """Tensor product of linear spaces."""
        A, B = Tens_A.shape, Tens_B.shape

        class Tens_AB(Tens([*A, *B])):

            @classmethod
            def pure(cls, x, y):
                """Pure tensor."""
                return cls(x | y)

        Tens_AB.__name__ = cls.name(Tens_A, Tens_B)
        Tens_AB.pure = Hom((Tens_A, Tens_B), Tens_AB)(Tens_AB.pure)
        return Tens_AB

    def __init__(self, Tens_A, Tens_B):
        pass

    @classmethod
    def fmap(cls, f, g):
        """Tensor product of matrices."""

        # --- read input matrices ---
        if f.data.is_sparse and g.data.is_sparse:
            F, G = f.data, g.data
        if f.data.is_sparse and not g.data.is_sparse:
            F, G = f.data, g.data.to_sparse()
        elif not f.data.is_sparse and g.data.is_sparse:
            F, G = f.data.to_sparse(), g.data
        else:
            F, G = f.data, g.data

        # --- domain and codomain ---
        src = cls(f.src, g.src)
        tgt = cls(f.tgt, g.tgt)
        Nf, Mf = F.shape
        Ng, Mg = G.shape

        # --- sparse tensor product ---
        if F.is_sparse and G.is_sparse:
            F, G = f.data.coalesce(), g.data.coalesce()
            # tensor product on indices
            ij, ab = F.indices(), G.indices()
            Vf, Vg = F.values(), G.values()
            IJ = ij.repeat_interleave(ab.shape[1], 1)
            AB = ab.repeat(1, ij.shape[1])
            XY = torch.tensor([Ng, Mg])[:, None] * IJ + AB
            val = Vf.repeat_interleave(Vg.shape[0], 0) * Vg.repeat(Vf.shape[0])
            # output sparse matrix
            shape = [Nf * Ng, Mf * Mg]
            data = torch.sparse_coo_tensor(XY, val, shape, device=F.device)

        # --- dense tensor product ---
        else:
            FG = (
                torch.outer(F.flatten(), G.flatten())
                .reshape([Nf, Mf, Ng, Mg])
                .transpose(1, 2)
                .reshape([Nf * Ng, Mf * Mg])
            )
            data = FG

        return Linear(src, tgt)(data)
