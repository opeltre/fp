import unittest

from fp.meta import TypeClass

class TestType(unittest.TestCase):

    def test_type(self):
        """ Test construction of type instances. """
        A = TypeClass("A", (str,), {})
        result = isinstance(A, type)
        self.assertTrue(A)

        class B(int, metaclass=TypeClass):
            pass
        result = isinstance(B, type)
        self.assertTrue(B)

    def test_cast(self):
        """ Test cast method. """
        Int = TypeClass("Int", (int,), {})
        result = Int.cast(3.5)
        expect = Int(3)
        self.assertEqual(expect, result)

        Str = TypeClass("Str", (str,), {})
        result = Str.cast(12)
        expect = Str("12")
        self.assertEqual(expect, result)
