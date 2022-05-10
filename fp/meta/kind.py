class Kind(type):
    """ Type kinds. """

    def __new__(cls, name, bases, dct):
        """ Create a kind. """
        T = super().__new__(cls, name, bases, dct)
        T.__str__   = lambda t: t.__name__
        T.__repr__  = lambda t: f"{type(t)} : {t.__name__}"
        return T

    def __repr__(self): 
        """ Show type name. """
        return f"{self} : {self.kind}"

    def __str__(self):
        return self.__name__.replace("Meta", "")
