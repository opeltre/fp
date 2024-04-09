from fp.meta import TypeClass, RingClass, AlgClass

#--- 

class Int(int, metaclass=RingClass):

    def __str__(self):
        return super().__repr__()

class Float(float, metaclass=AlgClass):
    
    def __str__(self):
        return super().__repr__()
