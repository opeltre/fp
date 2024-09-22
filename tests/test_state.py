import fp
from fp import Int, Str

class TestState: 

    St = fp.State(Str)

    def test_new(self): 
        StInt = self.St(Int)
        assert isinstance(StInt, fp.Type)

    def test_init(self):

        @self.St(Int)
        def length(s): 
            return "", len(s)
        
        assert isinstance(length, self.St(Int))
    
    def test_exec(self): 

        @self.St(Int)
        def length(s): 
            return "", len(s)

        assert length.exec("hello world") == ""
    
    def test_eval(self):

        @self.St(Int)
        def length(s): 
            return "", len(s)

        assert length.eval("hello world") == 11

    def test_run_is_call(self): 

        @self.St(Int)
        def length(s): 
            return "", len(s)

        assert length.run("hello") == length("hello")


