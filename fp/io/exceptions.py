
class Error(Exception):
    ...

class CastError(Error):

    def __init__(self, T, x):
        msg = f'\n  Could not cast {x} to {T}'
        super().__init__(msg)