import argparse
import os
import shutil
import time

import qha
from qha.calculator import *
#from qha.utils.out import save_x_tp, save_x_vt, save_to_output, make_starting_string, make_tp_info, make_ending_string
from qha.settings import from_yaml
from qha.utils.output import save_to_output, make_starting_string, make_tp_info, make_ending_string

import pathlib

import types

from qha.cli.program import QHAProgram

from qha.calculator2 import *
from qha.utils.units import QHAUnits
from .results_writer import TVFieldResultsWriter, TPFieldResultsWriter

units = QHAUnits()

class QHACalculator(QHAProgram):
    def __init__(self):
        super().__init__()
        self.settings = None
        self.start_time = time.time()

    def init_parser(self, parser):
        super().init_parser(parser)
        parser.add_argument('-s', '--settings', default='settings.yaml')
    
    def prompt(self, message: str):
        save_to_output(
            os.path.join(self.__get_output_directory_path(), 'output.txt'),
            message
        )
        print(message)

    def __save_temperature_pressure_info(self, tv_calc, pressure_sample_ratio: int):
        self.prompt(
            make_tp_info(
                tv_calc.temperature_array.magnitude[0],
                tv_calc.temperature_array.magnitude[-1 - 4],
                tv_calc.temperature_pressure_field_adapter.pressure_array.to(units.GPa).magnitude[0::pressure_sample_ratio][0],
                tv_calc.temperature_pressure_field_adapter.pressure_array.to(units.GPa).magnitude[0::pressure_sample_ratio][-1]
            )
        )
    
    def __save_starting_string(self):
        self.prompt(make_starting_string())
    
    def __save_ending_string(self):
        self.prompt(make_ending_string(time.time() - self.start_time))
    
    def __save_volume_range(self, v_ratio):
        if self.settings['high_verbosity']:
            self.prompt(
                'The volume range used in this calculation expanded x {0:6.4f}'.format(v_ratio)
            )
    
    def __get_output_directory_path(self):
        output_directory_path = self.settings['output_directory']
        return output_directory_path
    
    def __make_output_directory(self):
        output_directory_path = self.__get_output_directory_path()
        if os.path.exists(output_directory_path):
            shutil.rmtree(output_directory_path)
            # TODO: if it is a file
        os.makedirs(output_directory_path)
 
    __accepted_keys = [
        'same_phonon_dos','input',
        'calculate', 'static_only', 'energy_unit',
        'T_MIN', 'NT', 'DT', 'DT_SAMPLE',
        'P_MIN', 'NTV', 'DELTA_P', 'DELTA_P_SAMPLE',
        'volume_ratio', 'order', 'p_min_modifier',
        'T4FV', 'output_directory', 'plot_results', 'high_verbosity'
    ]
    
    def run(self, namespace):
        settings_file_path = namespace.settings
        input_settings = from_yaml(settings_file_path)

        self.settings = dict()
        for key in self.__accepted_keys:
            if key in input_settings.keys():
                self.settings[key] = input_settings[key]

        output_directory_path = self.__get_output_directory_path()
        self.__make_output_directory()

        self.__save_starting_string()

        calculator = TemperatureVolumeFieldCalculator(self.settings)

        print(self.settings)
        # TODO: find_negative_frequencies

        calculator.calculate()

        self.__save_temperature_pressure_info(calculator, int(self.settings['DELTA_P_SAMPLE'] / self.settings['DELTA_P']))

        self.__save_volume_range(calculator.v_ratio)

        tv_writer = TVFieldResultsWriter(
            output_directory_path,
            calculator,
            int(self.settings['DT_SAMPLE'] / self.settings['DT'])
        )
        tv_writer.write('P', 'p_tv_gpa.txt', units.GPa)
        tv_writer.write('F', 'f_tv_fitted_ev_ang3.txt', units.eV)

        raw_tv_writer = TVFieldResultsWriter(
            output_directory_path,
            calculator.helmholtz_free_energy_calculator,
            int(self.settings['DT_SAMPLE'] / self.settings['DT'])
        )
        raw_tv_writer.write('F', 'f_tv_nonfitted_ev_ang3.txt', units.eV)

        tp_writer = TPFieldResultsWriter(
            output_directory_path,
            calculator,
            int(self.settings['DELTA_P_SAMPLE'] / self.settings['DELTA_P'])
        )
        for prop_settings in self.settings['calculate']:
            print(prop_settings)
            tp_writer.write(
                prop_settings.get('prop'),
                prop_settings.get('output'),
                prop_settings.get('unit')
            )
        
        self.__save_ending_string()
    
