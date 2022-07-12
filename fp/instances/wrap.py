from fp.meta import Type, Functor, Arrow, Prod

class Wrap(Functor):
    """ 
    Type wrapper lifting selected methods to the contained value.
    

    The `lifts` class attribute is looked up to assign lifted methods.
    It expects a dictionary of method type signatures of the following form:

        lifts = { 'name' : (homtype: Type -> Type) }

    such that `homtype(A)` is the type of method `A.name`, e.g. 
        
        lifts = { 'add' : lambda A : Arrow((A, A), A)} 
    
    The output type `Wrap A` will inherit a method 'name' wrapping the 
    call on contained values.  
    """        

    def __new__(cls, A):

        class Wrap_A (Type):

            functor = cls 

            def __init__(self, data):
                if isinstance(data, A):
                    self.data = data
                elif "cast_data" in dir(self.__class__):
                    self.data = self.__class__.cast_data(data)
                else:
                    try: 
                        self.data = A(data)
                    except:
                        raise TypeError(
                            f"Received invalid input {data} : {type(data)} "+\
                            f"for Wrap {A} instance")
            
            def __repr__(self):
                return A.__str__(self.data)

            if '__eq__' in dir(A):
                def __eq__(self, other):
                    return self.data == other.data

            @classmethod
            def cast(cls, data):
                if isinstance(data, cls): 
                    return data
                T = type(data)
                if "functor" in dir(T) and "data" in dir(data):
                    return cls(data.data) 
                return cls(data)
        
        Wrap_A.lifts = {}

        return Wrap_A
    
    def __init__(Wrap_A, A):
        #--- Lift methods
        cls = Wrap_A.functor
        for name, homtype in cls.lifts.items():
            if not name in Wrap_A.lifts: 
                f  = homtype(A)(getattr(A, name))
                Wf = cls.fmap(f) if f.arity == 1 else cls.fmapN(f)
                setattr(Wrap_A, name, Wf)
                Wrap_A.lifts[name] = Wf

    @classmethod
    def fmap(cls, f):
        src, tgt = cls(f.src), cls(f.tgt)
        return Arrow(src, tgt)(
            lambda x: f(x.data)
        )

    @classmethod    
    def fmapN(cls, f):
        src = tuple([cls(si) for si in f.src.types])
        tgt = cls(f.tgt)
        map_f =  Arrow(src, tgt)(
            lambda *xs: f(*(x.data for x in xs))
        )
        map_f.__name__ = f'mapN {f.__name__}'
        return map_f    