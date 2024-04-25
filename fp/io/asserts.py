from .exceptions import CompositionError, TypeError

class asserts:

    def subclass(A, B):
        if A is not B and not issubclass(A, B):
            raise TypeError(f"{A} is not a subclass of {B}")

    def composable(*fs):
        pairs = zip(fs[:-1], fs[1:])
        for i, pair in enumerate(pairs):
            fst, snd = pair
            if not fst.tgt == snd.src:
                raise CompositionError(
                    f"Uncomposable pair at position {i}: {type(fst)} @ {type(snd)}"
                )
