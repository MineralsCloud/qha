#!/usr/bin/env python3

import os
import pathlib
import subprocess
import unittest

import numpy as np
import pandas as pd


class TestReadInput(unittest.TestCase):
    def setUp(self):
        self.dir = pathlib.Path('../../examples')
        self.run = 'qha-run'
        self.benchmark = 'results.benchmark'
        self.new_results_folder = 'results.bfm3'

    @staticmethod
    def listdir_nohidden(txtpath):
        for f in os.listdir(txtpath):
            if not f.startswith('.'):
                if f.find('_tp') > 0:
                    yield f

    def comparsion(self, path_results_benchmark, path_results_new):
        d = dict()
        for f in self.listdir_nohidden(path_results_benchmark):
            d.update({f: pd.read_csv(str(path_results_benchmark) + '/' + f, sep='\s+', index_col='T(K)\P(GPa)')})

        d0 = dict()
        for f in self.listdir_nohidden(path_results_new):
            d0.update({f: pd.read_csv(str(path_results_new) + '/' + f, sep='\s+', index_col='T(K)\P(GPa)')})

        for k, v in d.items():
            print(k + ':', np.max(np.abs(v.as_matrix() - d0[k].as_matrix())))

    def prepare_benchmark(self, path_results_benchmark):
        if not os.path.exists(path_results_benchmark):
            print(
                "{} has not been found, please generate the files for the benchmark, `mv *.txt results.benchmark` ".format(
                    self.benchmark))
            os.makedirs(path_results_benchmark)
            exit(1)
        else:
            print("make sure that the files in {} is correct".format(self.benchmark))

    def prepare_results_new(self, path_results_new, path_results, path_run_command):
        if not os.path.exists(path_results_new):
            os.makedirs(path_results_new)
            subprocess.run("qha-run", shell=True, cwd=path_run_command)
            com = "mv *.txt " + self.new_results_folder
            subprocess.run(com, shell=True, cwd=path_results)
        else:
            print("{} has been found, change a new name for the new_results_folder".format(self.new_results_folder))
            # exit(2)

    def test_silicon(self, foldername='silicon'):
        print("testing the examples/silicon")

        path_run_command = self.dir / foldername
        path_results = path_run_command / 'results'
        path_results_benchmark = path_results / self.benchmark
        path_results_new = path_results / self.new_results_folder

        self.prepare_benchmark(path_results_benchmark)
        self.prepare_results_new(path_results_new, path_results, path_run_command)

        self.comparsion(path_results_benchmark, path_results_new)

    def test_ice(self, foldername='ice VII'):
        print("testing the examples/ice VII")
        path_run_command = self.dir / foldername
        path_results = path_run_command / 'results'
        path_results_benchmark = path_results / self.benchmark
        path_results_new = path_results / self.new_results_folder

        self.prepare_benchmark(path_results_benchmark)
        self.prepare_results_new(path_results_new, path_results, path_run_command)

        self.comparsion(path_results_benchmark, path_results_new)

        print("testing the examples/ice VII, 4th order")
        self.comparsion(path_results / 'results.bmf4', path_results / 'results.bfm4')

        print("testing the examples/ice VII, 5th order")
        self.comparsion(path_results / 'results.bmf5', path_results / 'results.bfm5')


if __name__ == '__main__':
    unittest.main()
