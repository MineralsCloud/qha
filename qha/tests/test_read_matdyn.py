#!/usr/bin/env python3
# Created at Mar 15, 2018, by Qi Zhang

import unittest
import pathlib

from qha.readers.read_matdyn import read_matdyn


class TestReadMatdyn(unittest.TestCase):
    def setUp(self):
        self.dir = pathlib.Path('../../examples')

    def test_make_freq_array(self):
        file_path = [self.dir / 'silicon/make_input/V0.freq', self.dir / 'silicon/make_input/V+1.freq']
        print(file_path)
        freq = read_matdyn(file_path)
        self.assertEqual(freq.shape, (2, 16, 6))
