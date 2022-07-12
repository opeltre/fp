import torch

from .tensor import Tensor, WrapRing
from .shape  import Torus
from fp.meta import ArrowMeta, Arrow, Functor
from fp.meta import RingMeta

class Tens(Functor):
    
    def __new__(cls, A):

        class Field_A(Tensor):

            shape  = A
            domain = Torus(A)

           
            def __init__(self, data):
                S = self.__class__.shape
                if isinstance(data, Tensor):
                    data = data.data
                if not isinstance(data, torch.Tensor):
                    data = torch.tensor(data)
                if S == list(data.shape):
                    self.data = data
                elif len(data.shape) == 0:
                    self.data = data
                elif S[-len(data.shape):] == list(data.shape):
                    self.data = data
                else:
                    self.data = data.reshape(S)

            def __repr__(self):
                return (str(self.data)
                            .replace("tensor(", "")
                            .replace("\n       ", "\n")
                            .replace(")", ""))

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
                return(cls(torch.arange(cls.domain.size).view(cls.shape)))
            
            @classmethod
            def embed(cls, *ds):
                """ Linear embedding Tens B -> Tens A for B subface of A. 
                
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
                """ Partial integration Tens A -> Tens B for B subface of A. 

                    This linear map projects onto tensors of shape
                    `B = [A[di] for di in ds]` by:

                        g_b[xb] = sum_{xa[ds] = xb} g_a[xa]
                    
                    This is the pushforward of the coordinate map `cls.domain.res(*ds)` 
                    (acting on measures), and the adjoint of the algebra morphism `cls.embed(*ds)`.
                """
                return cls.embed(*ds).t()

        name  = cls.name(A)
        bases = (Tensor,)
        dct = dict(Field_A.__dict__)
        dct['shape']  = list(A)
        dct['domain'] = Torus(A)
        TA = RingMeta(name, bases, dct)
        return TA

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
        j = (g(i) if batch
                  else [g(ik) for ik in i])
        ij  = torch.stack([i.data, j.data])
        mat = Tensor.sparse([g.src.size, g.tgt.size], ij)
        return Linear(ms, ns)(mat)


class Linear(metaclass=ArrowMeta):

    def __new__(cls, A, B):

        NA = int(torch.tensor(A).prod())
        NB = int(torch.tensor(B).prod())

        class LinAB (Tens([NB, NA]), Arrow(Tens(A), Tens(B))):
            
            functor = Linear
            input = (A, B)

            def __init__(self, matrix, name=None):
                cls = self.__class__
                 # Tens([B, A]) attributes
                mat = matrix.data if isinstance(matrix, Tensor) else matrix
                if mat.is_sparse: mat = mat.coalesce()
                self.data = mat
                
                # Arrow(Tens([A]), Tens([B])) attributes
                self.call = lambda x : cls.matvec(matrix, x)
                if mat.is_sparse:
                    nnz = mat.indices().shape[-1]
                    self.__name__ = f'sparse {NB}x{NA} (nnz={nnz})'
                else:
                    self.__name__ = f'dense {NB}x{NA}' 
               
               
            @classmethod
            def matvec (cls, mat, x):
                """ Matrix vector product. """
                if isinstance(x, (Tensor, torch.Tensor)):
                    sx = list(x.data.shape)
                    src = list(cls.src.shape)
                    if sx == [cls.src.domain.size]:
                        if torch.is_complex(mat.data) and not torch.is_complex(x.data):
                            return tgt.field(mat.data @ x.data.cfloat())
                        return mat.data @ x.data
                    elif sx == src:
                        return mat.data @ x.data.view([-1])
                    elif sx[-len(src):] == src:
                        xT = x.data.view([-1, cls.src.size]).T
                        return (mat.data @ xT).T

            def t(self):
                """ Adjoint operator in Linear(B, A). """
                return Linear(B, A)(self.data.t())

            def __repr__(self):
                return self.__name__
        
        return LinAB

    def __init__(self, A, B):
        pass

    @classmethod
    def compose (cls, f, g):
        """ Composition of matrices. """
        if f.data.is_sparse and g.data.is_sparse:
            data = torch.sparse.mm(f.data, g.data)
        else:
            data = f.data @ g.data
        fg = cls(f.tgt.shape, g.src.shape)(data)
        return fg

    @classmethod
    def name(cls, A, B):
        shape = lambda S : 'x'.join(str(n) for n in S)
        return f'Linear {shape(A)} -> {shape(B)}'
