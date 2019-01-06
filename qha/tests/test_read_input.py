#!/usr/bin/env python3
# Created at Apr 17, 2018, by Qi Zhang

import pathlib
import unittest

import numpy as np

from qha.basic_io.read_input import read_input


class TestReadInput(unittest.TestCase):
    def setUp(self):
        self.dir = pathlib.Path('../../examples')

    def test_read_si_input(self):
        file_path = self.dir / 'silicon/input'
        nm, volumes, static_energies, frequencies, q_weights = read_input(file_path)
        self.assertEqual(nm, 2)
        np.testing.assert_array_equal(volumes,
                                      [320.5259, 311.4549, 302.5568, 293.8297, 285.2721, 276.8823, 268.6586, 260.5994,
                                       252.703, 244.9677, 237.392])

    def test_read_ice_input(self):
        for i in range(1, 53):
            file_path = self.dir / "{0}{1:02d}".format('ice VII/input_conf', i)
            nm, volumes, static_energies, frequencies, q_weights = read_input(file_path)
            self.assertEqual(nm, 16)


if __name__ == '__main__':
    unittest.main()
