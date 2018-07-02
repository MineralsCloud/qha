#!/usr/bin/env python3

import os
import pathlib

import qha
import qha.tools
from qha.plotting import Plotter
from qha.settings import from_yaml


class PlotHandler:
    def __init__(self, arguments_for_command: dict = {}):
        if not arguments_for_command:
            if not isinstance(arguments_for_command, dict):
                raise TypeError("The *arguments_for_command* argument must be a dictionary!")

            if not all(isinstance(k, str) for k in arguments_for_command.keys()):
                raise TypeError("The *arguments_for_command* argument's keys must be all strings!")

            if not all(isinstance(v, str) for v in arguments_for_command.values()):
                raise TypeError("The *arguments_for_command* argument's values must be all strings!")

        self._arguments_for_command = arguments_for_command
        self.file_settings = self._arguments_for_command['settings']

    def run(self):
        user_settings = {}  # save necessary info for plotting later
        settings = from_yaml(self.file_settings)

        for key in ('energy_unit', 'NT', 'DT', 'DT_SAMPLE', 'P_MIN', 'NTV', 'DELTA_P', 'DELTA_P_SAMPLE',
                    'calculate', 'T4FV', 'output_directory'):
            try:
                user_settings.update({key: settings[key]})
            except KeyError:
                continue

        if not os.path.exists(user_settings['output_directory']):
            raise FileNotFoundError("There is no results folder, please run: `qha-run` first! ")

        plotter = Plotter(user_settings)

        DESIRED_PRESSURES_GPa = qha.tools.arange(user_settings['P_MIN'], user_settings['NTV'], user_settings['DELTA_P'])
        user_settings.update({'DESIRED_PRESSURES_GPa': DESIRED_PRESSURES_GPa})

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
        user_settings.update({'f_tv_fitted': file_ftv_fitted})

        file_ftv_non_fitted = results_folder / 'f_tv_nonfitted_ev_ang3.txt'
        user_settings.update({'f_tv_non_fitted': file_ftv_non_fitted})

        file_ptv_gpa = results_folder / 'p_tv_gpa.txt'
        user_settings.update({'p_tv_gpa': file_ptv_gpa})

        plotter.fv_pv()

        for idx in user_settings['calculate']:
            if idx in ['F', 'G', 'H', 'U']:
                attr_name = calculation_option[idx] + '_' + user_settings['energy_unit']
                file_name = attr_name + '.txt'
                file_dir = results_folder / file_name
                user_settings.update({idx: file_dir})
                plotter.plot2file(idx)

            if idx == 'V':
                v_ang3 = calculation_option[idx] + '_' + 'ang3'
                file_name_ang3 = v_ang3 + '.txt'
                file_dir_ang3 = results_folder / file_name_ang3
                user_settings.update({idx: file_dir_ang3})
                plotter.plot2file(idx)

            if idx in ['Cv', 'Cp', 'Bt', 'Btp', 'Bs', 'alpha', 'gamma']:
                attr_name = calculation_option[idx]
                file_name = attr_name + '.txt'
                file_dir = results_folder / file_name
                user_settings.update({idx: file_dir})
                plotter.plot2file(idx)
