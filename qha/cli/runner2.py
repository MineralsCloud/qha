#!/usr/bin/env python3

import argparse
import os
import time

import qha
from qha.calculator import *
from qha.out import save_x_tp, save_x_vt, save_to_output, make_starting_string, make_tp_info, make_ending_string
from qha.settings import from_yaml
import pathlib

import types

from qha.cli.program import QHAProgram

from qha.calculator2 import *
from qha.units import QHAUnits

units = QHAUnits()

class QHARunner2(QHAProgram):
    def __init__(self):
        super().__init__()

    def init_parser(self, parser):
        super().init_parser(parser)
        parser.add_argument('-s', '--settings', default='settings.yaml')
    
    def run(self, namespace):
        start_time_total = time.time()

        user_settings = {}
        file_settings = namespace.settings
        settings = from_yaml(file_settings)

        for key in ('same_phonon_dos', 'input',
                    'calculate', 'static_only', 'energy_unit',
                    'T_MIN', 'NT', 'DT', 'DT_SAMPLE',
                    'P_MIN', 'NTV', 'DELTA_P', 'DELTA_P_SAMPLE',
                    'volume_ratio', 'order', 'p_min_modifier',
                    'T4FV', 'output_directory', 'plot_results', 'high_verbosity'):
            try:
                user_settings.update({key: settings[key]})
            except KeyError:
                continue

        # TODO: This line for test purpose only
        user_settings['output_directory'] = user_settings['output_directory'].replace('results', 'results-neue')

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
            calc = BasicTemperatureVolumeFieldCalculator(user_settings)
            print("You have single-configuration calculation assumed.")
        elif isinstance(user_input, dict):
            if user_settings['same_phonon_dos']:
                calc = SamePhononDOSTemperatureVolumeFieldCalculator(user_settings)
                print("You have multi-configuration calculation with the same phonon DOS assumed.")
            else:
                calc = DifferentPhononDOSTemperatureVolumeFieldCalculator(user_settings)
                print("You have multi-configuration calculation with different phonon DOS assumed.")
        else:
            raise ValueError("The 'input' in your settings in not recognized! It must be a dictionary or a list!")
        
        adapted = VolumeToPressureFieldAdapter(calc)

        save_to_output(
            user_settings['qha_output'],
            make_tp_info(
                calc.get_temperature_array().magnitude[0],
                calc.get_temperature_array().magnitude[-1 - 4],
                adapted.get_desired_pressures().to(units.GPa).magnitude[0],
                adapted.get_desired_pressures().to(units.GPa).magnitude[-1]
            )
        )

        calc.read_input()


        print("Caution: If negative frequencies found, they are currently treated as 0!")
        tmp = calc.find_negative_frequencies()
        if tmp is not None and not (tmp.T[-1].max() <= 2):  # Don't delete this parenthesis!
            if calc.get_frequencies().magnitude.ndim == 4:  # Multiple configuration
                for indices in tmp:
                    print("Found negative frequency in {0}th configuration {1}th volume {2}th q-point {3}th band".format(
                        *tuple(indices + 1)))
            elif calc.get_frequencies().magnitude.ndim == 3:  # Single configuration
                for indices in tmp:
                    print("Found negative frequency in {0}th volume {1}th q-point {2}th band".format(*tuple(indices + 1)))

        calc.calculate()
        calc.refine_grid()

        if user_settings['high_verbosity']:
            save_to_output(
                user_settings['qha_output'],
                'The volume range used in this calculation expanded x {0:6.4f}'.format(calc._v_ratio))

        calc.check_desired_pressure_status()

        temperature_array = calc.get_temperature_array().magnitude
        desired_pressures_gpa = calc.get_desired_pressures().to(units.GPa).magnitude
        temperature_sample = calc.get_temperature_sample_array().magnitude
        p_sample_gpa = calc.get_pressure_sample_array().to(units.GPa).magnitude

        results_folder = pathlib.Path(user_settings['output_directory'])

        calculation_option = {
            'F':     'f_tp',
            'G':     'g_tp',
            'H':     'h_tp',
            'U':     'u_tp',
            'V':     'v_tp',
            'Cv':    'cv_tp_jmolk',
            'Cp':    'cp_tp_jmolk',
            'Bt':    'bt_tp_gpa',
            'Btp':   'btp_tp',
            'Bs':    'bs_tp_gpa',
            'alpha': 'alpha_tp',
            'gamma': 'gamma_tp',
        }

        getter_options = {
            'F': 'get_helmholtz_free_energy',
            'G': 'get_gibbs_free_energy',
            'H': 'get_entropy',
            'U': 'get_internal_energy',
            'V': 'get_volume',
            'Cv': 'get_volume_specific_heat_capacity',
            'Cp': 'get_pressure_specific_heat_capacity',
            'Bt': 'get_isothermal_bulk_modulus',
            #'Btp': 'get_pressure_specific_heat_capacity',
            'Bs': 'get_adiabatic_bulk_modulus',
            'alpha': 'get_thermal_expansion_coefficient',
            'gamma': 'get_gruneisen_parameter',
        }

        default_units = {
            'Cv': units.J / units.kelvin,
            'Cp': units.J / units.kelvin,
            'Bt': units.GPa,
        }

        calculation_options = [
            {
                'key': 'holmholtz_free_energy',
                'alias': [
                    'F', 'holmholtz free energy'
                ],
                'getter': lambda c: c.get_helmholtz_free_energy(),
                'default_unit': units.Ryd,
                'per_unit': False
            },
            {
                'key': 'gibbs_free_energy',
                'alias': [
                    'G', 'gibbs free energy'
                ],
                'getter': lambda c: c.get_gibbs_free_energy(),
                'default_unit': units.Ryd,
                'per_unit': False
            },
            {
                'key': 'entropy',
                'alias': [
                    'H', 'entropy'
                ],
                'getter': lambda c: c.get_entropy(),
                'default_unit': units.Ryd,
                'per_unit': False
            },
            {
                'key': 'internal_energy',
                'alias': [
                    'U', 'internal energy'
                ],
                'getter': lambda c: c.get_internal_energy(),
                'default_unit': units.Ryd,
                'per_unit': False
            },
            {
                'key': 'volume',
                'alias': [
                    'V', 'volume'
                ],
                'getter': lambda c: c.get_volumes(),
                'default_unit': units.angstrom ** 3,
                'per_unit': False
            },
            {
                'key': 'volume_specific_heat_capacity',
                'alias': [
                    'Cv', 'volume specific heat capacity'
                ],
                'getter': lambda c: c.get_volume_specific_heat_capacity(),
                'default_unit': units.J / units.kelvin,
                'per_unit': True
            },
            {
                'key': 'pressure_specific_heat_capacity',
                'alias': [
                    'Cv', 'pressure specific heat capacity'
                ],
                'getter': lambda c: c.get_pressure_specific_heat_capacity(),
                'default_unit': units.J / units.kelvin,
                'per_unit': True
            },
            {
                'key': 'isothermal_bulk_modulus',
                'alias': [
                    'Bt', 'isothermal bulk modulus'
                ],
                'getter': lambda c: c.get_isothermal_bulk_modulus(),
                'default_unit': units.GPa,
                'per_unit': False
            },
            {
                'key': 'adiabatic_bulk_modulus',
                'alias': [
                    'Bs', 'adiabatic bulk modulus'
                ],
                'getter': lambda c: c.get_adiabatic_bulk_modulus(),
                'default_unit': units.GPa,
                'per_unit': False
            },
            {
                'key': 'thermal_expansion_coefficient',
                'alias': [
                    'alpha', 'thermal expansion coefficient'
                ],
                'getter': lambda c: c.get_thermal_expansion_coefficient(),
                'default_unit': units.kelvin ** -1,
                'per_unit': False
            },
            {
                'key': 'gruneisen_parameter',
                'alias': [
                    'gamma', 'gruneisen parameter'
                ],
                'getter': lambda c: c.get_gruneisen_parameter(),
                'default_unit': units.dimensionless,
                'per_unit': False
            },
            {
                'key': 'isothermal_bulk_modulus_pressure_derivative',
                'alias': [
                    'Btp', 'isothermal bulk modulus pressure derivative'
                ],
                'getter': lambda c: c.get_isothermal_bulk_modulus_pressure_derivative(),
                'default_unit': units.dimensionless,
                'per_unit': False
            },

        ]

        file_ftv_fitted = results_folder / 'f_tv_fitted_ev_ang3.txt'
        save_x_vt(
            calc.get_helmholtz_free_energy().to(units.eV).magnitude,
            temperature_array,
            calc.get_volumes().to(units.angstrom**3).magnitude,
            temperature_sample,
            file_ftv_fitted)

        file_ftv_non_fitted = results_folder / 'f_tv_nonfitted_ev_ang3.txt'
        save_x_vt(
            calc.get_coarse_helmholtz_free_energy().to(units.eV).magnitude,
            temperature_array,
            calc.get_coarse_volumes().to(units.angstrom**3).magnitude,
            temperature_sample,
            file_ftv_non_fitted
        )

        file_ptv_gpa = results_folder / 'p_tv_gpa.txt'
        save_x_vt(
            calc.get_pressures().to(units.GPa).magnitude,
            temperature_array,
            calc.get_volumes().to(units.angstrom**3).magnitude,
            temperature_sample,
            file_ptv_gpa
        )

        def get_prop(calc, name: str, unit=None):
            prop = next(
                prop for prop in calculation_options
                if name in prop['alias']
            )
            return prop['getter'](
                PerUnit(calc) if prop['per_unit'] else calc
            ).to(
                unit if unit else prop['default_unit']
            ).magnitude

        def write_tp_prop(name: str, file_dir, unit=None):
            save_x_tp(
                get_prop(adapted, name, unit),
                temperature_array,
                desired_pressures_gpa,
                p_sample_gpa,
                file_dir
            )

        for idx in calc.settings['calculate']:
            getter_name = getter_options[idx]
            if idx in ['F', 'G', 'H', 'U']:
                attr_name = calculation_option[idx] + '_' + calc.settings['energy_unit']
                file_name = attr_name + '.txt'
                file_dir = results_folder / file_name
                write_tp_prop(idx, file_dir, calc.settings['energy_unit'])

            if idx == 'V':
                v_bohr3 = calculation_option[idx] + '_' + 'bohr3'
                file_name_bohr3 = v_bohr3 + '.txt'
                file_dir_au = results_folder / file_name_bohr3
                v_ang3 = calculation_option[idx] + '_' + 'ang3'
                file_name_ang3 = v_ang3 + '.txt'
                file_dir_ang3 = results_folder / file_name_ang3

                write_tp_prop(idx, file_dir_au, units.Bohr**3)
                write_tp_prop(idx, file_dir_ang3, units.angstrom**3)

            if idx in ['Cv', 'Cp', 'Bt', 'Btp', 'Bs', 'alpha', 'gamma']:
                attr_name = calculation_option[idx]
                file_name = attr_name + '.txt'
                file_dir = results_folder / file_name
                write_tp_prop(idx, file_dir)

        end_time_total = time.time()
        time_elapsed = end_time_total - start_time_total
        save_to_output(user_settings['qha_output'], make_ending_string(time_elapsed))
