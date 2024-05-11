@struct
class NumpyAPI(Interface):
    
    module = np 

    Array = np.ndarray
    asarray = np.asarray

    dtypes = [
        "float:float32",
        "double:float64",
        "int:int32",
        "long:int64",
        "cfloat",
    ]

print(NumpyAPI._values_)

@struct
class JaxAPI(Interface):

    module = jax.numpy
    Array = jax.lib.xla_extension.ArrayImpl
    asarray = jax.numpy.asarray

    dtypes = NumpyAPI().dtypes[:-1] + [
        "cfloat:complex64",
        "cdouble:complex128",
    ]


@struct
class TorchAPI(Interface):
    
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

'''
class Backend(Stateful(Interface, NumpyAPI())):
    
    @classmethod
    def read_env(cls) -> str:
        env = "FP_BACKEND"
        s0 = os.environ[env] if env in os.environ else "torch"
'''

numpy = NumpyAPI()
