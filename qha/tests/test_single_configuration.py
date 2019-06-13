#!/usr/bin/env python3
# Created at Mar 26, 2018, by Qi Zhang

import unittest

from qha.single_configuration import ho_free_energy


class TestSingleConfiguration(unittest.TestCase):
    def test_ho_free_energy(self):
        self.assertEqual(ho_free_energy(0, 0), 0)
        self.assertEqual(ho_free_energy(1, -2), 0)
        self.assertAlmostEqual(ho_free_energy(0, 1000), 0.004556299262079407)
        self.assertAlmostEqual(ho_free_energy(100, 1000), 0.0045562989049199466)


if __name__ == '__main__':
    unittest.main()
