import torch
from fp import io
from fp.meta import Functor
from fp.cartesian import Type, Hom
from fp.instances import Int, List, Ring
from .tensor import Tensor
from .backend import Backend

class BaseShape(Tensor):

    d = 1
    n = [1]
    ns = torch.tensor([1])

    mod = torch.tensor([1])
    rmod = torch.tensor([1])
    size = 1

    def __iter__(self):
        return self.data.__iter__()

    @classmethod
    def cast(cls, js):
        if isinstance(js, Tensor):
            return cls.cast(js.data)
        t = (
            js.long()
            if isinstance(js, torch.Tensor)
            else torch.tensor(js, dtype=torch.long)
        )
        return cls(t % cls.ns)

    @classmethod
    def index(cls, js):
        """Row-major index of coordinates js.

            Tens d Long -> Tens 1 Long

        If a 2D tensor is given as coordinates,
        the first dimension is understood as batch
        dimension.
        """
        js = js.data
        if not len(js):
            return 0
        j0 = js[0]
        js = j0 if j0.dim() > 1 else js
        return (cls.mod * js).sum([-1])

    @classmethod
    def coords(cls, i):
        """Returns coordinates of row-major index.

        Tens 1 Long -> Tens d Long
        """
        if isinstance(i, int):
            if i >= cls.size or i < 0:
                raise IndexError(f"{cls} coords {i}")

        div = lambda a, b: torch.div(a, b, rounding_mode="floor")

        i = i.data
        if i.dim() == 0:
            out = torch.zeros([cls.dim], dtype=torch.long)
            for j, mj in enumerate(cls.mod):
                out[j] = div(i, mj)
                i = i % mj
            return out

        out = []
        for j, mj in enumerate(cls.mod):
            out += div(i[None, :], mj)
            i = i % mj
        return torch.stack(out).t() if len(out) else torch.tensor([[]])

    @classmethod
    def p(cls, d):
        """
        Index map of the projection on dimension d.

            Tens d Long -> Tens 1 Long
        """
        tgt = Torus([cls.n[d]])
        proj_d = Hom(cls, tgt)(lambda x: x.data.select(-1, d))
        proj_d.__name__ = f"p{d}"
        return proj_d

    @classmethod
    def res(cls, *ds):
        """
        Index map of the restriction on dimensions ds.

            Tens d Long -> Tens (d-k) Long
        """
        if not isinstance(ds, torch.Tensor):
            ds = torch.tensor(ds, dtype=torch.long)
        tgt = Torus([cls.n[d] for d in ds])

        @Hom(cls, tgt)
        def res_ds(x):
            return x.data.index_select(-1, ds)

        res_ds.__name__ = f'res {".".join(str(int(d)) for d in ds)}'
        return res_ds

    @classmethod
    def embed(cls, *ds):
        """
        Index map of the extension from dimensions ds by zeros.

            Tens (d-k) Long -> Tens d Long
        """
        src = Torus([cls.n[d] for d in ds])
        mat = torch.zeros([cls.dim, len(ds)], dtype=torch.long)
        for i, d in enumerate(ds):
            mat[d, i] = 1

        @Hom(src, cls)
        def emb_index(x):
            y = mat @ x if x.dim() == 1.0 else (mat @ x.T).T
            return int(cls.index(y))

        return emb_index


class Torus(Backend, Ring, metaclass=Functor):

    class Object(BaseShape):
        ...

    @classmethod
    def new(cls, A):

        name = cls._get_name_(A)
        bases = (BaseShape,)
        dct =  {"__name__": name}
        TA = Tensor._subclass_(name, bases, dct)
        io.log(("Torus new", TA, type(TA), type(TA) is cls), v=1)
        return TA
            
        # new shape instance
        if isinstance(A, type(None)):
            A = ()
        if not all(isinstance(ni, (int, torch.LongTensor)) for ni in A):
            raise TypeError("Expecting integer arguments")
        return super().new(A, (cls.Object,), {})
    
    def _post_new_(SA, A):
        dim = len(A)
        TA = torch.tensor(A)
        # attributes
        SA.dim = len(A)
        SA.n = tuple(A)
        SA.ns = torch.tensor(A)
        SA.shape = SA.n
        SA.mod = torch.tensor([torch.prod(TA[i + 1 :]) for i in range(dim)])
        SA.rmod = torch.tensor([torch.prod(TA[:-i]) for i in range(dim)])

        size = 1
        for ni in A:
            size *= ni
        SA.size = size
    
        flat = Torus((SA.size,)) if SA.dim > 1 else SA
        SA.index = Hom(SA, flat)(SA.index)
        SA.coords = Hom(flat, SA)(SA.coords)
        return SA
        '''
        '''

    def __init__(self, ns):
        pass

    @classmethod
    def fmap(cls, f):
        pass

    @classmethod
    def _get_name_(cls, ns):
        if isinstance(ns, type(None)):
            return f"Torus ."
        return f'Torus {"x".join(str(n) for n in ns)}'

    def __iter__(self):
        return self.n.__iter__()

    def __str__(self):
        return "(" + ",".join([str(ni) for ni in self.n]) + ")"
