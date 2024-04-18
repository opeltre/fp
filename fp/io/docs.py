import inspect

import fp.meta
import fp.instances

def document(Cls):
    if inspect.isclass(Cls) and hasattr(Cls, '_doc_'):
        Cls._doc_()
        return None
    for k, Ck in inspect.getmembers(Cls, inspect.isclass):
        document(Ck)
