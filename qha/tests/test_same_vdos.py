#!/usr/bin/env python3
# Created at Apr 4, 2018, by Qi Zhang

import unittest

import numpy as np

import qha.multi_configurations.same_phonon_dos as same_vdos
import qha.single_configuration as single_configuration
from qha.readers import read_input


class TestSameVDOS(unittest.TestCase):
    def setUp(self):
        # Assume one single configuration duplicated by 10 time, and compare the results with a single configuration.
        # They should be the same.
        self.configurations_num = 10
        _, self.volumes, self.static_energies, self.frequencies, self.q_weights = read_input('data/olivine/input.txt')
        self.multi_config_static_energies = np.repeat(self.static_energies, self.configurations_num).reshape(
            len(self.static_energies), self.configurations_num)

    def test_free_energy(self):
        as_single_config = single_configuration.free_energy(1000, self.q_weights, self.static_energies,
                                                            self.frequencies)

        as_multi_config_method1 = same_vdos.PartitionFunction(1000, self.multi_config_static_energies,
                                                              [1 / self.configurations_num] * self.configurations_num,
                                                              self.q_weights, self.frequencies).derive_free_energy()

        as_multi_config_method2 = same_vdos.FreeEnergy(1000, self.multi_config_static_energies,
                                                       [1 / self.configurations_num] * self.configurations_num,
                                                       self.q_weights, self.frequencies).total

        np.testing.assert_array_almost_equal(as_single_config, as_multi_config_method1)
        np.testing.assert_array_equal(as_single_config, as_multi_config_method2)
        print(self.multi_config_static_energies)
        print(self.multi_config_static_energies.shape)