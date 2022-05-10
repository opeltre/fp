from fp.meta import TypeMeta, RingMeta, AlgMeta

#--- 

class Int(int, metaclass=RingMeta):
    pass 

class Float(float, metaclass=AlgMeta):
    pass