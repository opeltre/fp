import functools 

def cache(f):
    """
    Cache a callable (e.g. type constructor) yet call it on unhashables.
    """
    f_ = functools.cache(f)
    def cached(*xs, **ys):
        try:
            return f_(*xs, **ys)
        except:
            return f(*xs, **ys)
    return cached
