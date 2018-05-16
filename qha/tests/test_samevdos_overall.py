#!/usr/bin/env python3

import os
import pathlib
import subprocess
import unittest

import numpy as np
import pandas as pd


class TestOverallRun(unittest.TestCase):
    def setUp(self):
        self.root_directory = pathlib.Path('../../examples')
        self.command = 'qha-run'
        self.fixed_directory = 'results.benchmark'
        self.new_results_directory = 'results.same_vdos_new01'

    @staticmethod
    def listdir_nohidden(txt_path):
        for f in os.listdir(txt_path):
            if not f.startswith('.'):
                if f.find('_tp') > 0:
                    yield f

    def compare_results(self, path_results_benchmark, path_results_new):
        d = dict()
        for f in self.listdir_nohidden(path_results_benchmark):
            d.update({f: pd.read_csv(str(path_results_benchmark) + '/' + f, sep='\s+', index_col='T(K)\P(GPa)')})

        d0 = dict()
        for f in self.listdir_nohidden(path_results_new):
            d0.update({f: pd.read_csv(str(path_results_new) + '/' + f, sep='\s+', index_col='T(K)\P(GPa)')})

        for k, v in d.items():
            print(k + ':', np.max(np.abs(v.as_matrix() - d0[k].as_matrix())))

    def prepare_results_new(self, path_results_new, path_results, path_run_command):
        os.makedirs(path_results_new, exist_ok=False)
        subprocess.run(self.command, shell=True, cwd=path_run_command)
        command = "mv *.txt " + self.new_results_directory
        subprocess.run(command, shell=True, cwd=path_results)

    def test_samevdos(self, test_directory='results/same_vdos_example_ol'):

        print("testing the results/same_vdos_example_ol same vdos ")
        path_run_command = self.root_directory / test_directory
        path_results = path_run_command / 'results'
        path_results_fixed = path_results / self.fixed_directory

        path_run_command = self.root_directory / test_directory
        path_results = path_run_command / 'results'
        self.compare_results(path_results_fixed, path_results / 'results.same_vdos_new01')
        self.compare_results(path_results / 'results.same_vdos_new', path_results / 'results.same_vdos_new01')
        self.compare_results(path_results / 'results.diff_vdos', path_results / 'results.diff_vdos_new')


if __name__ == '__main__':
    unittest.main()
