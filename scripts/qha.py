#!/usr/bin/env python3

import argparse
import os
import time

import qha
from qha.calculator import Calculator, SamePhDOSCalculator, DifferentPhDOSCalculator
from qha.out import save_x_tp, save_x_vt, save_to_output, make_starting_string, make_tp_info, make_ending_string
from qha.plot import QHAPlot
from qha.settings import from_yaml

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--settings', default='settings.yaml')
parser.add_argument('-v', '--version', action='version', version="current qha version: {0}".format(qha.__version__))
namespace = parser.parse_args()


def main():
    start_time_total = time.time()
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

    save_to_output(user_settings['qha_output'], make_starting_string())

    user_input = user_settings['input']

    if isinstance(user_input, str):
        calc = Calculator(user_settings)
        print("You have single-configuration calculation assumed.")
    elif isinstance(user_input, dict):  # Then it will be multi-configuration calculation.
        if user_settings['same_phonon_dos']:
            calc = SamePhDOSCalculator(user_settings)
            print("You have multi-configuration calculation with the same phonon DOS assumed.")
        else:
            calc = DifferentPhDOSCalculator(user_settings)
            print("You have multi-configuration calculation with different phonon DOS assumed.")
    else:
        raise ValueError("The 'input' in your settings in not recognized! It must be a dictionary or a list!")

    save_to_output(user_settings['qha_output'], make_tp_info(calc.temperature_array[0], calc.temperature_array[-1 - 4],
                                                             calc.desired_pressures_gpa[0],
                                                             calc.desired_pressures_gpa[-1]))

    calc.read_input()
    calc.refine_grid()

    if user_settings['high_verbosity']:
        save_to_output(user_settings['qha_output'],
                       'The volume range used in this calculation expanded x {0:6.4f}'.format(calc.v_ratio))

    calc.desired_pressure_status()

    plotter = QHAPlot(user_settings)

    T = calc.temperature_array
    DESIRED_PRESSURES_GPa = calc.desired_pressures_gpa
    DELTA_P_SAMPLE = calc.settings['DELTA_P_SAMPLE']
    DELTA_P = calc.settings['DELTA_P']

    T_SAMPLE = calc.temperature_sample_array
    P_SAMPLE_GPa = calc.pressure_sample_array

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
    save_x_vt(calc.f_tv_ev, T, calc.finer_volumes_ang3, T_SAMPLE, file_ftv_fitted)
    user_settings.update({'f_tv_fitted': file_ftv_fitted})

    file_ftv_non_fitted = results_folder + 'f_tv_nonfitted_ev_ang3.txt'
    save_x_vt(calc.vib_ev, T, calc.volumes_ang3, T_SAMPLE, file_ftv_non_fitted)
    user_settings.update({'f_tv_non_fitted': file_ftv_non_fitted})

    file_ptv_gpa = results_folder + 'p_tv_gpa.txt'
    save_x_vt(calc.p_tv_gpa, T, calc.finer_volumes_ang3, T_SAMPLE, file_ptv_gpa)
    user_settings.update({'p_tv_gpa': file_ptv_gpa})

    plotter.fv_pv()

    for idx in calc.settings['calculate']:
        if idx in ['F', 'G', 'H', 'U']:
            attr_name = calculation_option[idx] + '_' + calc.settings['energy_unit']
            file_dir = results_folder + attr_name + '.txt'
            save_x_tp(getattr(calc, attr_name), T, DESIRED_PRESSURES_GPa, P_SAMPLE_GPa, file_dir)
            user_settings.update({idx: file_dir})
            plotter.plot2file(idx)

        if idx == 'V':
            v_bohr3 = calculation_option[idx] + '_' + 'bohr3'
            file_dir_au = results_folder + v_bohr3 + '.txt'
            v_ang3 = calculation_option[idx] + '_' + 'ang3'
            file_dir_ang3 = results_folder + v_ang3 + '.txt'

            save_x_tp(getattr(calc, v_bohr3), T, DESIRED_PRESSURES_GPa, P_SAMPLE_GPa, file_dir_au)
            save_x_tp(getattr(calc, v_ang3), T, DESIRED_PRESSURES_GPa, P_SAMPLE_GPa, file_dir_ang3)
            user_settings.update({idx: file_dir_ang3})

            plotter.plot2file(idx)

        if idx in ['Cv', 'Cp', 'Bt', 'Btp', 'Bs', 'alpha', 'gamma']:
            attr_name = calculation_option[idx]
            file_dir = results_folder + attr_name + '.txt'
            save_x_tp(getattr(calc, attr_name), T, DESIRED_PRESSURES_GPa, P_SAMPLE_GPa, file_dir)
            user_settings.update({idx: file_dir})
            plotter.plot2file(idx)
    end_time_total = time.time()
    time_elapsed = end_time_total - start_time_total
    save_to_output(user_settings['qha_output'], make_ending_string(time_elapsed))
