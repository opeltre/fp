from colorama import Fore

WARN = Fore.MAGENTA + "/!\\" + Fore.RESET
RULE = Fore.YELLOW + "-" * 50 + Fore.RESET + "\n"

class Error(Exception): 

    def __init__(self, msg):
        super().__init__(RULE + msg)

class KeyError(Error):
    ...

class TypeError(Error):

    def __init__(self, name , x, Tx):
        msg = f"\n> Invalid type for " + name + ": "
        msg += f"\n      got {x}: {type(x)}, expected {Tx}"
        super().__init__(msg)

class CastError(Error):

    def __init__(self, T, x):
        msg = f"\n  Could not cast {x} to {T}"
        super().__init__(msg)

class ConstructorError(Error):

    def __init__(self, name, T, As):
        msg = f"\n\t{T}.new{As}"
        super().__init__(msg)

class CompositionError(Error):

    def __init__(self, fst, snd, *tail, op="and"):
        msg = f"\n Uncomposable pair: {type(fst)} {op} {type(snd)}"
        super().__init__(msg + " ".join(tail))
