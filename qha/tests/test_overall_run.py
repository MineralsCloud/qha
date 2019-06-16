#!/usr/bin/env python3

import os
import pathlib
import unittest

import numpy as np
import pandas as pd


class TestOverallRun(unittest.TestCase):
    def setUp(self):
        self.root_directory = pathlib.Path(__file__).parent.parent.parent / 'examples'
        self.fixed_directory = pathlib.Path(__file__).parent.parent.parent / 'qha_old/'

    @staticmethod
    def listdir_nohidden(txt_path):
        for f in os.listdir(txt_path):
            if not f.startswith('.') and f.find('_tp') > 0:
                yield f

    def compare_results(self, path_results_benchmark, path_results_new):
        d = dict()
        for f in self.listdir_nohidden(path_results_benchmark):
            d.update({f: pd.read_csv(str(path_results_benchmark) + '/' + f, sep='\s+', index_col='T(K)\P(GPa)')})

        d0 = dict()
        for f in self.listdir_nohidden(path_results_new):
            d0.update({f: pd.read_csv(str(path_results_new) + '/' + f, sep='\s+', index_col='T(K)\P(GPa)')})

        for k, v in d.items():
            # print(k + ':', np.max(np.abs(v.values() - d0[k].values())))
            print(k + ':')
            np.testing.assert_array_almost_equal(v.values(), d0[k].values(), decimal=3)

    def test_silicon(self, test_directory='silicon'):
        print("testing the examples/silicon")

        path_results = self.root_directory / test_directory / 'results'
        path_results_fixed = self.fixed_directory / test_directory / 'results'

        self.compare_results(path_results_fixed, path_results)

    def test_ice(self, test_directory='ice VII'):
        print("testing the examples/ice VII")

        path_results = self.root_directory / test_directory / 'results'
        path_results_fixed = self.fixed_directory / test_directory / 'results'

        self.compare_results(path_results_fixed, path_results)


if __name__ == '__main__':
    unittest.main()
