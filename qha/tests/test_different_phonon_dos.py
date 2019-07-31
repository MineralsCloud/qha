#!/usr/bin/env python3

import os
import unittest
from pathlib import Path

import numpy as np
from qha.calculator import DifferentPhDOSCalculator
from qha.multi_configurations.different_phonon_dos import PartitionFunction
from qha.settings import from_yaml


class TestPartitionFunction(unittest.TestCase):
    def setUp(self) -> None:
        os.chdir(Path(__file__).parent.parent.parent / 'examples/ice VII/')
        self.user_settings = {}
        settings = from_yaml("settings.yaml")

        for key in ('input', 'calculation',
                    'thermodynamic_properties', 'static_only', 'energy_unit',
                    'T_MIN', 'NT', 'DT', 'DT_SAMPLE',
                    'P_MIN', 'NTV', 'DELTA_P', 'DELTA_P_SAMPLE',
                    'volume_ratio', 'order', 'p_min_modifier',
                    'T4FV', 'output_directory', 'high_verbosity'):
            try:
                self.user_settings.update({key: settings[key]})
            except KeyError:
                continue
        self.calculator = DifferentPhDOSCalculator(self.user_settings)
        self.calculator.read_input()
        self.partition_function = PartitionFunction(1000, self.calculator.degeneracies, self.calculator.q_weights,
                                                    self.calculator.static_energies, self.calculator._volumes,
                                                    self.calculator.frequencies)

    def test_parse_settings(self):
        self.assertDictEqual(self.user_settings, {
            'input': {'input_01': 6, 'input_02': 96, 'input_03': 96, 'input_04': 24, 'input_05': 24, 'input_06': 192,
                      'input_07': 384, 'input_08': 24, 'input_09': 384, 'input_10': 96, 'input_11': 192,
                      'input_12': 384, 'input_13': 48, 'input_14': 96, 'input_15': 48, 'input_16': 96, 'input_17': 96,
                      'input_18': 384, 'input_19': 384, 'input_20': 48, 'input_21': 384, 'input_22': 96,
                      'input_23': 384, 'input_24': 96, 'input_25': 192, 'input_26': 192, 'input_27': 192,
                      'input_28': 384, 'input_29': 192, 'input_30': 192,
                      'input_31': 96, 'input_32': 192, 'input_33': 192, 'input_34': 384, 'input_35': 384,
                      'input_36': 192, 'input_37': 24, 'input_38': 48, 'input_39': 96, 'input_40': 48, 'input_41': 384,
                      'input_42': 12, 'input_43': 96, 'input_44': 48, 'input_45': 192, 'input_46': 12, 'input_47': 96,
                      'input_48': 48, 'input_49': 6, 'input_50': 96, 'input_51': 24, 'input_52': 24},
            'calculation': 'different phonon dos',
            'thermodynamic_properties': ['F', 'G', 'U', 'H', 'V', 'alpha', 'gamma', 'Cp', 'Cv', 'Bt', 'Btp', 'Bs'],
            'static_only': False, 'energy_unit': 'ry', 'T_MIN': 0, 'NT': 401, 'DT': 1, 'DT_SAMPLE': 1, 'P_MIN': 0,
            'NTV': 701, 'DELTA_P': 0.1, 'DELTA_P_SAMPLE': 1, 'order': 3, 'p_min_modifier': 1.0, 'T4FV': ['0', '300'],
            'output_directory': './results/', 'high_verbosity': True})

    def test_parameters(self):
        self.assertEqual(self.calculator.degeneracies, (
            6, 96, 96, 24, 24, 192, 384, 24, 384, 96, 192, 384, 48, 96, 48, 96, 96, 384, 384, 48, 384, 96, 384, 96, 192,
            192, 192, 384, 192, 192, 96, 192, 192, 384, 384, 192, 24, 48, 96, 48, 384, 12, 96, 48, 192, 12, 96, 48, 6,
            96, 24, 24))
        self.assertEqual(self.calculator.frequencies.shape,
                         (52, 6, 1, 144))  # frequency on each (configuration, volume, q-point and mode)
        np.testing.assert_array_equal(self.calculator.q_weights,
                                      np.ones((52, 1)))  # We only have Γ points, whose weight is 1.
        np.testing.assert_array_equal(self.calculator.volumes,
                                      [2290.7412, 2179.0756, 1666.2973, 1362.8346, 1215.6528, 1120.4173])
        self.assertEqual(self.calculator._volumes.shape, (52, 6))
        self.assertEqual(self.calculator.static_energies.shape,
                         (52, 6))  # static energy on each (configuration, volume)

    def test_partition_function(self):
        self.assertEqual(self.partition_function.unaligned_free_energies_for_each_configuration.shape,
                         (52, 6))  # (# of configurations, # of volumes)
        self.assertEqual(self.partition_function.aligned_free_energies_for_each_configuration.shape,
                         (52, 6))  # (# of configurations, # of volumes)
        self.assertEqual(self.partition_function.partition_functions_for_each_configuration.shape,
                         (52, 6))  # (# of configurations, # of volumes)
        self.assertEqual(self.partition_function.partition_functions_for_all_configurations.shape,
                         (6,))  # (# of volumes,)
        np.testing.assert_array_almost_equal(self.partition_function.get_free_energies(),
                                             [-550.74580132, -550.70964062, -550.37436235, -549.87365787, -549.43586034,
                                              -549.03029969])
