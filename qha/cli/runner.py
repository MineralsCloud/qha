#!/usr/bin/env python3
"""
.. module cli.runner
   :platform: Unix, Windows, Mac, Linux
.. moduleauthor:: Chenxing Luo <chenxing.luo@columbia.edu>
.. moduleauthor:: Tian Qin <qinxx197@umn.edu>
.. moduleauthor:: Qi Zhang <qz2280@columbia.edu>
"""

import os
import pathlib
import time

from qha.calculator import Calculator, SamePhDOSCalculator, DifferentPhDOSCalculator
from qha.basic_io.out import save_x_tp, save_x_tv, save_to_output, make_starting_string, make_tp_info, make_ending_string
from qha.settings import from_yaml
from .handler import QHACommandHandler


class QHARunner(QHACommandHandler):
    def __init__(self):
        super().__init__()

        self.settings = None
        self.start_time = None

    def init_parser(self, parser):
        super().init_parser(parser)
        parser.add_argument('settings', type=str)

    def run(self, namespace):
        start_time_total = time.time()

        user_settings = {}
        file_settings = namespace.settings
        settings = from_yaml(file_settings)

        for key in ('input', 'calculation',
                    'thermodynamic_properties', 'static_only', 'energy_unit',
                    'T_MIN', 'NT', 'DT', 'DT_SAMPLE',
                    'P_MIN', 'NTV', 'DELTA_P', 'DELTA_P_SAMPLE',
                    'volume_ratio', 'order', 'p_min_modifier',
                    'T4FV', 'output_directory', 'high_verbosity'):
            try:
                user_settings.update({key: settings[key]})
            except KeyError:
                continue

        if not os.path.exists(user_settings['output_directory']):
            os.makedirs(user_settings['output_directory'])

        user_settings.update({'qha_output': os.path.join(
            user_settings['output_directory'], 'output.txt')})

        try:
            os.remove(user_settings['qha_output'])
        except OSError:
            pass

        save_to_output(user_settings['qha_output'], make_starting_string())

        calculation_type = user_settings['calculation'].lower()
        if calculation_type == 'single':
            calc = Calculator(user_settings)
            print("You have single-configuration calculation assumed.")
        elif calculation_type == 'same phonon dos':
            calc = SamePhDOSCalculator(user_settings)
            print(
                "You have multi-configuration calculation with the same phonon DOS assumed.")
        elif calculation_type == 'different phonon dos':
            calc = DifferentPhDOSCalculator(user_settings)
            print(
                "You have multi-configuration calculation with different phonon DOS assumed.")
        else:
            raise ValueError("The 'calculation' in your settings in not recognized! It must be one of:"
                             "'single', 'same phonon dos', 'different phonon dos'!")

        save_to_output(user_settings['qha_output'],
                       make_tp_info(calc.temperature_array[0], calc.temperature_array[-1 - 4],
                                    calc.desired_pressures_gpa[0],
                                    calc.desired_pressures_gpa[-1]))

        calc.read_input()

        print("Caution: If negative frequencies found, they are currently treated as 0!")
        tmp = calc.where_negative_frequencies
        # Don't delete this parenthesis!
        if tmp is not None and not (tmp.T[-1].max() <= 2):
            if calc.frequencies.ndim == 4:  # Multiple configuration
                for indices in tmp:
                    print(
                        "Found negative frequency in {0}th configuration {1}th volume {2}th q-point {3}th band".format(
                            *tuple(indices + 1)))
            elif calc.frequencies.ndim == 3:  # Single configuration
                for indices in tmp:
                    print(
                        "Found negative frequency in {0}th volume {1}th q-point {2}th band".format(*tuple(indices + 1)))

        calc.refine_grid()

        if user_settings['high_verbosity']:
            save_to_output(user_settings['qha_output'],
                           'The volume range used in this calculation expanded x {0:6.4f}'.format(calc.v_ratio))

        calc.desired_pressure_status()

        temperature_array = calc.temperature_array
        desired_pressures_gpa = calc.desired_pressures_gpa
        temperature_sample = calc.temperature_sample_array
        p_sample_gpa = calc.pressure_sample_array

        results_folder = pathlib.Path(user_settings['output_directory'])

        calculation_option = {'F': 'f_tp',
                              'G': 'g_tp',
                              'H': 'h_tp',
                              'U': 'u_tp',
                              'V': 'v_tp',
                              'Cv': 'cv_tp_jmolk',
                              'Cp': 'cp_tp_jmolk',
                              'Bt': 'bt_tp_gpa',
                              'Btp': 'btp_tp',
                              'Bs': 'bs_tp_gpa',
                              'alpha': 'alpha_tp',
                              'gamma': 'gamma_tp',
                              }

        file_ftv_fitted = results_folder / 'f_tv_fitted_ev_ang3.txt'
        save_x_tv(calc.f_tv_ev, temperature_array,
                  calc.finer_volumes_ang3, temperature_sample, file_ftv_fitted)

        file_ftv_non_fitted = results_folder / 'f_tv_nonfitted_ev_ang3.txt'
        save_x_tv(calc.vib_ev, temperature_array, calc.volumes_ang3,
                  temperature_sample, file_ftv_non_fitted)

        file_ptv_gpa = results_folder / 'p_tv_gpa.txt'
        save_x_tv(calc.p_tv_gpa, temperature_array,
                  calc.finer_volumes_ang3, temperature_sample, file_ptv_gpa)

        file_stv_j = results_folder / 's_tv_j.txt'
        save_x_tv(calc.s_tv_j, temperature_array,
                  calc.finer_volumes_ang3, temperature_sample, file_stv_j)

        for idx in calc.settings['thermodynamic_properties']:
            if idx in ['F', 'G', 'H', 'U']:
                attr_name = calculation_option[idx] + \
                    '_' + calc.settings['energy_unit']
                file_name = attr_name + '.txt'
                file_dir = results_folder / file_name
                save_x_tp(getattr(calc, attr_name), temperature_array,
                          desired_pressures_gpa, p_sample_gpa, file_dir)

            if idx == 'V':
                v_bohr3 = calculation_option[idx] + '_' + 'bohr3'
                file_name_bohr3 = v_bohr3 + '.txt'
                file_dir_au = results_folder / file_name_bohr3
                v_ang3 = calculation_option[idx] + '_' + 'ang3'
                file_name_ang3 = v_ang3 + '.txt'
                file_dir_ang3 = results_folder / file_name_ang3

                save_x_tp(getattr(calc, v_bohr3), temperature_array,
                          desired_pressures_gpa, p_sample_gpa, file_dir_au)
                save_x_tp(getattr(calc, v_ang3), temperature_array,
                          desired_pressures_gpa, p_sample_gpa, file_dir_ang3)

            if idx in ['Cv', 'Cp', 'Bt', 'Btp', 'Bs', 'alpha', 'gamma']:
                attr_name = calculation_option[idx]
                file_name = attr_name + '.txt'
                file_dir = results_folder / file_name
                save_x_tp(getattr(calc, attr_name), temperature_array,
                          desired_pressures_gpa, p_sample_gpa, file_dir)

        end_time_total = time.time()
        time_elapsed = end_time_total - start_time_total
        save_to_output(user_settings['qha_output'],
                       make_ending_string(time_elapsed))
