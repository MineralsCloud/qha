#!/usr/bin/env python3
# Created at Apr 17, 2018, by Qi Zhang

import unittest

import numpy as np

from qha.readers.read_input import read_input


class TestReadInput(unittest.TestCase):
    def test_read_ice(self):
        for i in range(1, 53):
            read_input("{0}{1:02d}".format('data/ice VII/input_conf', i))

    def test_read_mgo(self):
        nm, volumes, static_energies, frequencies, q_weights = read_input('data/mgo/input.txt')
        self.assertEqual(volumes.shape, (11,))
        self.assertEqual(static_energies.shape, (11,))
        self.assertEqual(frequencies.shape, (11, 256, 162))
        self.assertEqual(nm, 1)
        np.testing.assert_array_equal(
            [1, 8, 8, 8, 8, 8, 8, 8, 8, 8, 4, 6, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 12,
             6, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 12, 6, 24, 24, 24, 24, 24, 24, 24, 24, 24,
             24, 24, 24, 24, 12, 6, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 12, 6, 24, 24, 24, 24, 24, 24, 24, 24,
             24, 12, 6, 24, 24, 24, 24, 24, 24, 24, 12, 6, 24, 24, 24, 24, 24, 12, 6, 24, 24, 24, 12, 6, 24, 12, 3, 24,
             48, 48, 48, 48, 48, 48, 48, 24, 24, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 24, 24, 48, 48, 48,
             48, 48, 48, 48, 48, 48, 48, 48, 24, 24, 48, 48, 48, 48, 48, 48, 48, 48, 48, 24, 24, 48, 48, 48, 48, 48, 48,
             48, 24, 24, 48, 48, 48, 48, 48, 24, 24, 48, 48, 48, 24, 24, 48, 24, 12, 24, 48, 48, 48, 48, 48, 24, 24, 48,
             48, 48, 48, 48, 48, 48, 48, 48, 24, 24, 48, 48, 48, 48, 48, 48, 48, 24, 24, 48, 48, 48, 48, 48, 24, 24, 48,
             48, 48, 24, 24, 48, 24, 12, 24, 48, 48, 48, 24, 24, 48, 48, 48, 48, 48, 24, 24, 48, 48, 48, 24, 24, 48, 24,
             12, 24, 48, 24, 24, 48, 24, 12, 6], q_weights)

    def test_read_si(self):
        nm, volumes, static_energies, frequencies, q_weights = read_input('data/si/input.txt')
        self.assertEqual(volumes)

    def test_read_olivine(self):
        read_input('data/olivine/input.txt')

    def test_read_iron(self):
        read_input('data/hcp iron/input.txt')
