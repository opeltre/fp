import inspect

import fp.meta
import fp.instances
from .log import log

def document(Cls):
    if inspect.isclass(Cls) and hasattr(Cls, '_doc_'):
        try: 
            Cls._doc_()
            return None
        except:
            ...
    if inspect.ismodule(Cls):
        for k, Ck in inspect.getmembers(Cls, inspect.isclass):
            log(f"documenting {k}", v=2)
            document(Ck)
