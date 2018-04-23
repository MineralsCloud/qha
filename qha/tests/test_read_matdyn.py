#!/usr/bin/env python3
# Created at Mar 15, 2018, by Qi Zhang

import unittest

from qha.readers.read_matdyn import read_matdyn


class TestReadMatdyn(unittest.TestCase):
    def setUp(self):
        self.files = ['data/hcp_Fe_56/P0_Fe56.freq', 'data/hcp_Fe_56/P50_Fe56.freq', 'data/hcp_Fe_56/P100_Fe56.freq']

    def test_make_freq_array(self):
        freq = read_matdyn(self.files)
        self.assertEqual(freq.shape, (3, 484, 6))
