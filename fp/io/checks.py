from .exceptions import CompositionError 

def assertComposable(*fs):
    pairs = zip(fs[:-1], fs[1:])
    for i, pair in enumerate(pairs):
        fst, snd = pair
        if not fst.tgt == snd.src:
            raise CompositionError(
                f"Uncomposable pair at position {i}: {type(fst)} @ {type(snd)}"
            )
