import unittest

from qha.v2p import _lagrange4


class TestLagrange4(unittest.TestCase):
    # Examples from here: https://www.geeksforgeeks.org/lagrange-interpolation-formula/
    def test_case1(self):
        test1_x = 7
        expected_y1 = -11
        y1 = _lagrange4(test1_x, 1, 2, 3, 5, 10, 4, 4, 7)
        self.assertEqual(y1, expected_y1, "Case 1 failed")

    def test_case2(self):
        test2_x = 10
        expected_y2 = 17
        y2 = _lagrange4(test2_x, 5, 6, 7, 8, 12, 13, 14, 15)
        self.assertEqual(y2, expected_y2, "Case 2 failed")


if __name__ == "__main__":
    unittest.main()
