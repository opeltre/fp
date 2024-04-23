import colorama 
from colorama import Fore, Style

VERBOSITY = 0

def log(text, v=0, prefix=None):
    if v <= VERBOSITY:
        if prefix is None:
            prefix = "    " * v + ">" if v > 0 else ""
        if type(text) is tuple:
            text = " ".join(str(t) for t in text)
        print(color(prefix, v), color(text))

def color(text, c=None):

    COLORS = [
        'WHITE', 
        'YELLOW',
        'GREEN', 
        'CYAN',
        'MAGENTA',
        'RED',
    ]

    if c is None:
        return Style.DIM + text + Style.NORMAL
    if isinstance(c, int):
        c = COLORS[c]
    prefix = getattr(Fore, c)
    return prefix + text + Fore.RESET
