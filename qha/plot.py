#!/usr/bin/env python3

import argparse
import os

import qha
from qha.calculator import Calculator, SamePhDOSCalculator, DifferentPhDOSCalculator
from qha.plotting import Plotter
from qha.settings import from_yaml

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--settings', default='settings.yaml')
parser.add_argument('-v', '--version', action='version', version="current qha version: {0}".format(qha.__version__))
namespace = parser.parse_args()


def main():
    user_settings = {}  # save necessary info for plotting later

    file_settings = namespace.settings

    settings = from_yaml(file_settings)

    for key in ('same_phonon_dos', 'input', 'volume_energies',
                'calculate', 'static_only', 'energy_unit',
                'NT', 'DT', 'DT_SAMPLE',
                'P_MIN', 'NTV', 'DELTA_P', 'DELTA_P_SAMPLE',
                'calculate', 'volume_ratio', 'order', 'p_min_modifier',
                'T4FV', 'output_directory', 'plot_results', 'high_verbosity'):
        try:
            user_settings.update({key: settings[key]})
        except KeyError:
            continue

    if not os.path.exists(user_settings['output_directory']):
        os.makedirs(user_settings['output_directory'])

    user_settings.update({'qha_output': os.path.join(user_settings['output_directory'], 'output.txt')})

    try:
        os.remove(user_settings['qha_output'])
    except OSError:
        pass

    user_input = user_settings['input']

    if isinstance(user_input, str):
        calc = Calculator(user_settings)
    elif isinstance(user_input, dict):  # Then it will be multi-configuration calculation.
        if user_settings['same_phonon_dos']:
            calc = SamePhDOSCalculator(user_settings)
        else:
            calc = DifferentPhDOSCalculator(user_settings)
    else:
        raise ValueError("The 'input' in your settings in not recognized! It must be a dictionary or a list!")

    calc.read_input()
    calc.refine_grid()

    calc.desired_pressure_status()

    plotter = Plotter(user_settings)

    DESIRED_PRESSURES_GPa = calc.desired_pressures_gpa


    user_settings.update({'DESIRED_PRESSURES_GPa': DESIRED_PRESSURES_GPa})

    results_folder = user_settings['output_directory']

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

    # check F(T,V) at the first place
    file_ftv_fitted = results_folder + 'f_tv_fitted_ev_ang3.txt'
    user_settings.update({'f_tv_fitted': file_ftv_fitted})

    file_ftv_non_fitted = results_folder + 'f_tv_nonfitted_ev_ang3.txt'
    user_settings.update({'f_tv_non_fitted': file_ftv_non_fitted})

    file_ptv_gpa = results_folder + 'p_tv_gpa.txt'
    user_settings.update({'p_tv_gpa': file_ptv_gpa})

    plotter.fv_pv()

    for idx in user_settings['calculate']:
        if idx in ['F', 'G', 'H', 'U']:
            attr_name = calculation_option[idx] + '_' + user_settings['energy_unit']
            file_dir = results_folder + attr_name + '.txt'
            user_settings.update({idx: file_dir})
            plotter.plot2file(idx)

        if idx == 'V':
            v_bohr3 = calculation_option[idx] + '_' + 'bohr3'
            file_dir_au = results_folder + v_bohr3 + '.txt'
            v_ang3 = calculation_option[idx] + '_' + 'ang3'
            file_dir_ang3 = results_folder + v_ang3 + '.txt'

            user_settings.update({idx: file_dir_ang3})

            plotter.plot2file(idx)

        if idx in ['Cv', 'Cp', 'Bt', 'Btp', 'Bs', 'alpha', 'gamma']:
            attr_name = calculation_option[idx]
            file_dir = results_folder + attr_name + '.txt'
            user_settings.update({idx: file_dir})
            plotter.plot2file(idx)
