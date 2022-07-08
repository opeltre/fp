import torch

from .tensor import Tensor
from .shape  import Torus
from fp.meta import ArrowMeta, Arrow, Functor
from fp.meta import RingMeta

class Tens(Functor):
    
    class Scalar (Tensor):

        shape = Torus([])

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
            return(cls(torch.arange(cls.shape.size).view(shape.n)))
        
        @classmethod
        def embed(cls, *ds):
            res = Torus(cls.shape).res(*ds)
            src, tgt = res.src, res.tgt
            return Tens.cofmap(tgt.index @ res @ src.coords)

    def __new__(cls, shape):
        name = cls.name(shape)
        bases, dct = cls.Scalar.__bases__, dict(cls.Scalar.__dict__)
        dct['shape'] = shape
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
        i = torch.arange(f.src.size)
        j = (f(i) if batch
                  else [f(ik) for ik in i])
        ij  = torch.stack([i.data, j.data])
        mat = Tensor.sparse([f.src.size, f.tgt.size], ij)
        return Linear(f.tgt.size, f.src.size)(mat)

class Linear(metaclass=ArrowMeta):

    def __new__(cls, A, B):
        
        class LinAB (Tens([B, A]), Arrow(Tens([A]), Tens([B]))):
            
            functor = Linear
            input = (A, B)

            def __init__(self, matrix, name=f'mat {B}x{A}'):
                cls = self.__class__
                # Arrow(Tens([A]), Tens([B])) attributes
                self.call = lambda x : cls.matvec(matrix, x)
                self.__name__ = name
                # Tens([B, A]) attributes
                mat = matrix.data if isinstance(matrix, Tensor) else matrix
                super().__init__(mat)

            
            @classmethod
            def matvec (cls, mat, x):
                if isinstance(x, Tensor):
                    return mat.data @ x.data
                elif isinstance(x, torch.Tensor):
                    return mat.data @ x.data
            
            def __repr__(self):
                return self.__name__
        
        return LinAB

    def __init__(self, A, B):
        pass

    @classmethod
    def compose (cls, f, g):
        """ Composition of matrices """
        return cls(f.tgt.shape[0], g.src.shape[0])(f.data @ g.data)

    @classmethod
    def name(cls, A, B):
        shape = lambda S : 'x'.join(str(n) for n in S)
        return f'Linear {A} -> {B}'