from fp.meta import TypeMeta, RingMeta, AlgMeta

#--- 

class Int(int, metaclass=RingMeta):

    def __str__(self):
        return super().__repr__()

class Float(float, metaclass=AlgMeta):
    
    def __str__(self):
        return super().__repr__()