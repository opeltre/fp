class Arrow: 
    """ Typed functions. """
    
    def __init__(self, arr, f, name="\u03bb"):
        """ Create a function f : arr[0] -> arr[-1]. """
        self.src    = arr[0]
        self.tgt    = arr[-1]
        self.call   = f
        self.name   = name
        self.__name__ = name

    def __call__(self, x):
        """ Check input type then call. """
        if isinstance(x, self.src):
            return self.call(x)
        try:
            return self.call(self.src(x))
        except:
            raise TypeError(f"Input not castable to {self.src}")


    def __matmul__(self, other):
        """ Composition of functions. """
        if not self.src == other.tgt:
            raise TypeError(f"Uncomposable pair"\
                    + f"{(self.src, self.tgt)} @"\
                    + f"{(other.src, other.tgt)}")
        src, tgt = other.src, self.tgt
        name = f"{self.name} . {other.name}"
        return Arrow([src, tgt], name, lambda x: other(self(x))) 

    def __repr__(self):
        return f"{self.name} : {self.src.__name__} -> {self.tgt.__name__}"