import unittest

from fp.meta import TypeMeta

class TestType(unittest.TestCase):

    def test_type(self):
        """ Test construction of type instances. """
        A = TypeMeta("A", (str,), {})
        result = isinstance(A, type)
        self.assertTrue(A)

        class B(int, metaclass=TypeMeta):
            pass
        result = isinstance(B, type)
        self.assertTrue(B)

    def test_cast(self):
        """ Test cast method. """
        Int = TypeMeta("Int", (int,), {})
        result = Int.cast(3.5)
        expect = Int(3)
        self.assertEqual(expect, result)

        Str = TypeMeta("Str", (str,), {})
        result = Str.cast(12)
        expect = Str("12")
        self.assertEqual(expect, result)
