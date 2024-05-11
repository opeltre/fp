import colorama

colorama.init()

#--- Method decorators for type pretty-printing 

def repr_method(rep):
    def _rep_(x):
        tx = f"{type(x)} : "
        indent = len(tx)
        rx = rep(x)
        tx = colorama.Style.DIM + tx + colorama.Style.NORMAL
        if rx[:len(tx)] == tx:
            return rx
        else:
            return tx + rx.replace("\n", "\n" + " " * indent)

    return _rep_

def str_method(show):
    return lambda x: show(x)


def showStruct(struct):
    out = "{\n"
    N = len(struct)
    for i, (k, vk) in enumerate(struct.items()):
        prefix = "    " + str(k) + ": "
        val = str(vk).replace("\n", "\n" + " " * 2) #len(prefix)  
        out += prefix + val + ("\n" if i == N - 1 else ",\n")
    return out + "}"
