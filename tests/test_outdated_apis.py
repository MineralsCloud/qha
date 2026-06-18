import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pandas as pd

from qha.cli.handler import QHACommandHandler
from qha.cli.parser import QHAArgumentParser
from qha.plotting import Plotter


class DummyHandler(QHACommandHandler):
    aliases = ()

    def init_parser(self, parser):
        return None

    def run(self, namespace):
        return None


class DummyEntryPoint:
    def __init__(self, name, loaded):
        self.name = name
        self._loaded = loaded

    def load(self):
        return self._loaded


class EntryPointsWithSelect:
    def __init__(self, plugins):
        self._plugins = plugins

    def select(self, **kwargs):
        if kwargs.get("group") == "qha.plugins":
            return self._plugins
        return []


class TestParserPluginLoading(unittest.TestCase):
    def test_load_plugins_with_select_api(self):
        parser = QHAArgumentParser()
        plugin = DummyEntryPoint(name="dummy", loaded=DummyHandler)
        with patch(
            "qha.cli.parser.importlib_metadata.entry_points",
            return_value=EntryPointsWithSelect([plugin]),
        ):
            parser.load_plugins()
        self.assertIn("dummy", parser.handlers)

    def test_load_plugins_with_mapping_api(self):
        parser = QHAArgumentParser()
        plugin = DummyEntryPoint(name="dummy", loaded=DummyHandler)
        with patch(
            "qha.cli.parser.importlib_metadata.entry_points",
            return_value={"qha.plugins": [plugin]},
        ):
            parser.load_plugins()
        self.assertIn("dummy", parser.handlers)


class TestPlotterNumPyCompatibility(unittest.TestCase):
    def test_fv_pv_works_without_asfarray(self):
        with TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            fitted_path = tmp_path / "f_tv_fitted.txt"
            non_fitted_path = tmp_path / "f_tv_non_fitted.txt"
            pressure_path = tmp_path / "p_tv_gpa.txt"

            data = pd.DataFrame({10.0: [1.0, 2.0], 11.0: [1.5, 2.5]}, index=[0.0, 100.0])
            data.index.name = "T(K)\\V(A^3)"
            data.to_csv(fitted_path, sep=" ")
            data.to_csv(non_fitted_path, sep=" ")
            data.to_csv(pressure_path, sep=" ")

            plotter = Plotter(
                {
                    "T4FV": [0.0, 100.0],
                    "f_tv_fitted": str(fitted_path),
                    "f_tv_non_fitted": str(non_fitted_path),
                    "p_tv_gpa": str(pressure_path),
                    "DESIRED_PRESSURES_GPa": [0.0, 1.0],
                    "output_directory": str(tmp_path),
                }
            )
            plotter.fv_pv()

            self.assertTrue((tmp_path / "FVT_PVT.pdf").exists())


if __name__ == "__main__":
    unittest.main()
