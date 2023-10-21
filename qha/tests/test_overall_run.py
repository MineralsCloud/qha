#!/usr/bin/env python3

import os
import pathlib
import subprocess
import unittest

import numpy as np
import pandas as pd


class TestOverallRun(unittest.TestCase):
    def setUp(self):
        self.root_directory = pathlib.Path(__file__).parent.parent.parent / "examples"
        self.command = "qha run"
        self.fixed_directory = "results.benchmark"
        self.new_results_directory = "results.plot"

    @staticmethod
    def listdir_nohidden(txt_path):
        for f in os.listdir(txt_path):
            if not f.startswith(".") and f.find("_tp") > 0:
                yield f

    def compare_results(self, path_results_benchmark, path_results_new):
        d = dict()
        for f in self.listdir_nohidden(path_results_benchmark):
            d.update(
                {
                    f: pd.read_csv(
                        str(path_results_benchmark) + "/" + f,
                        sep="\s+",
                        index_col="T(K)\P(GPa)",
                    )
                }
            )

        d0 = dict()
        for f in self.listdir_nohidden(path_results_new):
            d0.update(
                {
                    f: pd.read_csv(
                        str(path_results_new) + "/" + f,
                        sep="\s+",
                        index_col="T(K)\P(GPa)",
                    )
                }
            )

        for k, v in d.items():
            print(k + ":", np.max(np.abs(v.as_matrix() - d0[k].as_matrix())))

    def prepare_results_new(self, path_results_new, path_results, path_run_command):
        os.makedirs(path_results_new, exist_ok=False)
        subprocess.run(self.command, shell=True, cwd=path_run_command)
        command = "mv *.txt " + self.new_results_directory
        subprocess.run(command, shell=True, cwd=path_results)

    def test_silicon(self, test_directory="silicon"):
        print("testing the examples/silicon")

        path_run_command = self.root_directory / test_directory
        path_results = path_run_command / "results"
        path_results_fixed = path_results / self.fixed_directory
        path_results_new = path_results / self.new_results_directory

        # self.prepare_results_new(path_results_new, path_results, path_run_command)

        self.compare_results(path_results_fixed, path_results_new)

    def test_ice(self, test_directory="ice VII"):
        print("testing the examples/ice VII")

        path_run_command = self.root_directory / test_directory
        path_results = path_run_command / "results"
        path_results_benchmark = path_results / self.fixed_directory
        path_results_new = path_results / self.new_results_directory

        # self.prepare_results_new(path_results_new, path_results, path_run_command)
        #
        self.compare_results(path_results_benchmark, path_results_new)

        # print("testing the examples/ice VII, 3rd order")
        # self.compare_results(path_results / 'results.bmf3', path_results / 'results.bfm3')
        #
        # print("testing the examples/ice VII, 4th order")
        # self.compare_results(path_results / 'results.bmf4', path_results / 'results.bfm4')
        #
        # print("testing the examples/ice VII, 5th order")
        # self.compare_results(path_results / 'results.bmf5', path_results / 'results.bfm5')


if __name__ == "__main__":
    unittest.main()
