import torch

from .tensor import Tensor, WrapRing
from .shape import Torus
from fp.meta import HomClass, Hom, FunctorClass, BifunctorClass
from fp.meta import RingClass


class Tens(metaclass=FunctorClass):
    
    @classmethod
    def new(cls, A):

        class Field_A(Tensor):

            shape = A
            domain = Torus(A)

            def __init__(self, data):
                S = self.__class__.shape
                if isinstance(data, Tensor):
                    data = data.data
                if not isinstance(data, torch.Tensor):
                    data = torch.tensor(data)
                if S == tuple(data.shape) or S == list(data.shape):
                    self.data = data
                elif len(data.shape) == 0:
                    self.data = data
                elif S[-len(data.shape) :] == list(data.shape):
                    self.data = data
                else:
                    self.data = data.reshape(S)

            def otimes(self, other):
                """
                Tensor product of two instances.

                The tensor product xy of vectors x and y is defined by:

                    xy[i, j] = x[i] * y[j]

                In general, if x : Tens(A) and y : Tens(B) then xy
                is of type Tens([*A, *B])
                """
                TA, TB = self.__class__, other.__class__
                TAB = cls([*TA.shape, *TB.shape])
                xy = Tensor.otimes(self, other)
                return TAB(xy)

            @classmethod
            def zeros(cls, **ks):
                return cls(torch.zeros(cls.shape, **ks))

            @classmethod
            def ones(cls, **ks):
                return cls(torch.ones(cls.shape, **ks))

            @classmethod
            def randn(cls, **ks):
                return cls(torch.randn(cls.shape, **ks))

            @classmethod
            def rand(cls, **ks):
                return cls(torch.rand(cls.shape, **ks))

            @classmethod
            def range(cls):
                return cls(torch.arange(cls.domain.size).view(cls.shape))

            @classmethod
            def embed(cls, *ds):
                """Linear embedding Tens B -> Tens A for B subface of A.

                This algebra morphishm extends a tensor on the restriction
                `B = [A[di] for di in ds]` by:

                    f_a[di] = f_b[i] for i, di in enumerate(d)
                    f_a[dj] = 0      for dj not in d

                This is the pullback of the coordinate map `cls.domain.res(*ds)`,
                and the linear adjoint of `cls.proj(*ds)`.
                """
                res = cls.domain.res(*ds)
                return Tens.cofmap(res)

            @classmethod
            def proj(cls, *ds):
                """Partial integration Tens A -> Tens B for B subface of A.

                This linear map projects onto tensors of shape
                `B = [A[di] for di in ds]` by:

                    g_b[xb] = sum_{xa[ds] = xb} g_a[xa]

                This is the pushforward of the coordinate map `cls.domain.res(*ds)`
                (acting on measures), and the adjoint of the algebra morphism `cls.embed(*ds)`.
                """
                return cls.embed(*ds).t()

        name = cls.name(A)
        bases = (Tensor,)
        dct = dict(Field_A.__dict__)
        dct["shape"] = list(A)
        dct["domain"] = Torus(A)
        TA = RingClass(name, bases, dct)
        return TA
    
    def __init__(cls, A):
        ...

    @classmethod
    def name(cls, shape):
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


class Linear(metaclass=HomClass):
    """
    Linear maps types, containing dense or sparse matrices.

    The homtype `Linear(A, B)` represents the category structure
    on linear spaces obtained by the `Tens` constructor.

    The arguments `A` and `B` can either be given as tensor shapes
    or as associated tensor types e.g.

        A, B = Tens([2, 3]), Tens([4])
        assert Linear(A, B) == Linear([2, 3], [4])

    Linear map instances inherit from the Hom class, overriding
    composition and application by matrix-matrix and matrix-vector
    products respectively.
    """

    def __new__(cls, A, B):

        if isinstance(A, RingClass):
            A = A.shape
        if isinstance(B, RingClass):
            B = B.shape
        NA = int(torch.tensor(A).prod())
        NB = int(torch.tensor(B).prod())

        class LinAB(Tens([NB, NA]), Hom(Tens(A), Tens(B))):

            functor = Linear
            input = (A, B)

            def __init__(self, matrix, name=None):
                cls = self.__class__
                # Tens([B, A]) attributes
                mat = matrix.data if isinstance(matrix, Tensor) else matrix
                if mat.is_sparse:
                    mat = mat.coalesce()
                self.data = mat

                # Hom(Tens([A]), Tens([B])) attributes
                self.call = lambda x: cls.matvec(matrix, x)
                if mat.is_sparse:
                    nnz = mat.indices().shape[-1]
                    self.__name__ = f"sparse {NB}x{NA} (nnz={nnz})"
                else:
                    self.__name__ = f"dense {NB}x{NA}"

            @classmethod
            def matvec(cls, mat, x):
                """Matrix vector product."""
                if isinstance(x, (Tensor, torch.Tensor)):
                    sx = list(x.shape)
                    src = list(cls.src.shape)
                    M, X = mat, (x.data if isinstance(x, Tensor) else x)
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
                        ns = sx[:-len(src)]
                        xT = X.view([-1, n1]).T
                        return (M @ xT).T.view([*ns, *cls.tgt.shape])
                    print(sx, src, x.shape)
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
                return Linear(B, A)(self.data.t())

            def __repr__(self):
                return self.__name__

        return LinAB

    def __init__(self, A, B):
        pass

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

    @classmethod
    def compose(cls, f, g):
        """Composition of matrices."""
        if f.data.is_sparse and g.data.is_sparse:
            data = torch.sparse.mm(f.data, g.data)
        else:
            data = f.data @ g.data
        fg = cls(f.tgt.shape, g.src.shape)(data)
        return fg

    @classmethod
    def name(cls, A, B):
        if isinstance(A, RingClass):
            A = A.shape
        if isinstance(B, RingClass):
            B = B.shape
        shape = lambda S: "x".join(str(n) for n in S)
        return f"Linear {shape(A)} -> {shape(B)}"

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


class Otimes(metaclass=BifunctorClass):
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
