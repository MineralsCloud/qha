#!/usr/bin/env python3
"""
.. module cli.plotter
   :platform: Unix, Windows, Mac, Linux
.. moduleauthor:: Chenxing Luo <chenxing.luo@columbia.edu>
.. moduleauthor:: Tian Qin <qinxx197@umn.edu>
.. moduleauthor:: Qi Zhang <qz2280@columbia.edu>
"""

import os
import pathlib

import qha.tools
from qha.cli.handler import QHACommandHandler
from qha.plotting import Plotter
from qha.settings import from_yaml


class QHAPlotter(QHACommandHandler):
    def __init__(self):
        super().__init__()

    def init_parser(self, parser):
        super().init_parser(parser)
        parser.add_argument('settings', type=str)
        parser.add_argument('--outdir', type=str, help='output directory')

    def run(self, namespace):
        user_settings = {}  # save necessary info for plotting later
        file_settings = namespace.settings
        settings = from_yaml(file_settings)

        for key in ('energy_unit', 'NT', 'DT', 'DT_SAMPLE', 'P_MIN', 'NTV', 'DELTA_P', 'DELTA_P_SAMPLE',
                    'thermodynamic_properties', 'T4FV', 'output_directory'):
            try:
                user_settings.update({key: settings[key]})
            except KeyError:
                raise KeyError("Key '{0}' is not set in your settings!")

        if not os.path.exists(user_settings['output_directory']):
            raise FileNotFoundError("There is no results folder, please run: `qha-run` first! ")

        plotter = Plotter(user_settings)

        desired_pressures_gpa = qha.tools.arange(user_settings['P_MIN'], user_settings['NTV'], user_settings['DELTA_P'])
        user_settings.update({'DESIRED_PRESSURES_GPa': desired_pressures_gpa})

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

        for idx in user_settings['thermodynamic_properties']:
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
