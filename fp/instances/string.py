from fp.meta import TypeClass

class Str(str, metaclass=TypeClass): 

    def __str__(self):
        return f"'{super().__str__()}'"
