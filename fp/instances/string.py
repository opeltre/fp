from fp.meta import TypeMeta

class Str(str, metaclass=TypeMeta): 

    def __str__(self):
        return f"'{super().__str__()}'"