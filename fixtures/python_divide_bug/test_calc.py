import unittest

from calc import divide


class DivideTests(unittest.TestCase):
    def test_divide_regular_case(self) -> None:
        self.assertEqual(divide(8, 2), 4)

    def test_divide_by_zero_raises(self) -> None:
        with self.assertRaises(ZeroDivisionError):
            divide(8, 0)


if __name__ == "__main__":
    unittest.main()
