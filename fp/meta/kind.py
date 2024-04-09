from colorama import Fore

class Kind(type):
    """ Type kinds. """

    def __new__(cls, name, bases, dct):
        """ Create a kind. """
        T = super().__new__(cls, name, bases, dct)
        T.__str__   = lambda t: t.__name__
        T.__repr__  = lambda t: (Fore.MAGENTA + f"{type(t)} : " 
                                + Fore.RESET + f"{t.__name__}")
        return T

    def __repr__(self): 
        """ Show type name. """
        return f"{self} : " + Fore.YELLOW + f"{self.kind}" + Fore.RESET

    def __str__(self):
        return self.__name__
