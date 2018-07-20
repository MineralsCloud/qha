#!/usr/bin/env python3

import pathlib

from qha.calculator.per_unit import PerMole
from qha.utils.out import save_x_tv, save_x_tp
from qha.utils.units import QHAUnits

units = QHAUnits()


class ResultsWriter:
    def __init__(self, results_dir: str):
        self.results_directory_path = pathlib.Path(results_dir)

    def get_output_file_path(self, file_name):
        return self.results_directory_path / file_name

    def write(self):
        raise NotImplementedError()


class FieldResultsWriter(ResultsWriter):
    def __init__(self, results_dir: str, calculator):
        super().__init__(results_dir)
        self.calculator = calculator

    __calculation_options = [

        {
            'key': 'holmholtz_free_energy',
            'alias': [
                'F', 'holmholtz free energy'
            ],
            'getter': lambda c: c.helmholtz_free_energies,
            'default_unit': units.Ryd,
            'per_mole': False
        },
        {
            'key': 'gibbs_free_energy',
            'alias': [
                'G', 'gibbs free energy'
            ],
            'getter': lambda c: c.gibbs_free_energies,
            'default_unit': units.Ryd,
            'per_mole': False
        },
        {
            'key': 'entropy',
            'alias': [
                'H', 'entropy'
            ],
            'getter': lambda c: c.entropies,
            'default_unit': units.Ryd,
            'per_mole': False
        },
        {
            'key': 'internal_energy',
            'alias': [
                'U', 'internal energy'
            ],
            'getter': lambda c: c.internal_energies,
            'default_unit': units.Ryd,
            'per_mole': False
        },
        {
            'key': 'volume_specific_heat_capacity',
            'alias': [
                'Cv', 'volume specific heat capacity'
            ],
            'getter': lambda c: c.volume_specific_heat_capacities,
            'default_unit': units.J / units.kelvin,
            'per_mole': True
        },
        {
            'key': 'pressure_specific_heat_capacity',
            'alias': [
                'Cp', 'pressure specific heat capacity'
            ],
            'getter': lambda c: c.pressure_specific_heat_capacities,
            'default_unit': units.J / units.kelvin,
            'per_mole': True
        },
        {
            'key': 'isothermal_bulk_modulus',
            'alias': [
                'Bt', 'isothermal bulk modulus'
            ],
            'getter': lambda c: c.isothermal_bulk_moduli,
            'default_unit': units.GPa,
            'per_mole': False
        },
        {
            'key': 'adiabatic_bulk_modulus',
            'alias': [
                'Bs', 'adiabatic bulk modulus'
            ],
            'getter': lambda c: c.adiabatic_bulk_moduli,
            'default_unit': units.GPa,
            'per_mole': False
        },
        {
            'key': 'thermal_expansion_coefficient',
            'alias': [
                'alpha', 'thermal expansion coefficient'
            ],
            'getter': lambda c: c.thermal_expansion_coefficients,
            'default_unit': units.kelvin ** -1,
            'per_mole': False
        },
        {
            'key': 'gruneisen_parameter',
            'alias': [
                'gamma', 'gruneisen parameter'
            ],
            'getter': lambda c: c.gruneisen_parameters,
            'default_unit': units.dimensionless,
            'per_mole': False
        },
        {
            'key': 'isothermal_bulk_modulus_pressure_derivative',
            'alias': [
                'Btp', 'isothermal bulk modulus pressure derivative'
            ],
            'getter': lambda c: c.isothermal_bulk_modulus_pressure_derivatives,
            'default_unit': units.dimensionless,
            'per_mole': False
        },
        {
            'key': 'volume',
            'alias': [
                'V', 'volume'
            ],
            'getter': lambda c: c.volumes,
            'default_unit': units.angstrom ** 3,
            'per_mole': False
        },
        {
            'key': 'pressure',
            'alias': [
                'P', 'pressure'
            ],
            'getter': lambda c: c.pressures,
            'default_unit': units.GPa,
            'per_mole': False
        },
    ]

    def get_prop(self, name: str, unit=None):
        try:
            prop = next(prop for prop in self.__calculation_options if name in prop['alias'])
        except StopIteration:
            raise RuntimeError('Desired property name not found.')
        return prop['getter'](
            PerMole(self.calculator) if prop['per_mole'] else self.calculator
        ).to(
            unit if unit else prop['default_unit']
        ).magnitude

    def write(self):
        raise NotImplementedError()


class TVFieldResultsWriter(FieldResultsWriter):
    def __init__(self, results_dir: str, calculator, temperature_sample_ratio: int):
        super().__init__(results_dir, calculator)
        self.temperature_sample_ratio = temperature_sample_ratio

    def write(self, prop_name, file_name, unit=None):
        save_x_tv(
            self.get_prop(prop_name, unit),
            self.calculator.temperature_array.to(units.kelvin).magnitude,
            self.calculator.volume_array.to(units.angstrom ** 3).magnitude,
            self.calculator.temperature_array.to(units.kelvin).magnitude[0::self.temperature_sample_ratio],
            self.get_output_file_path(file_name)
        )


class TPFieldResultsWriter(FieldResultsWriter):
    def __init__(self, results_dir: str, calculator, pressure_sample_ratio: int):
        super().__init__(results_dir, calculator.temperature_pressure_field_adapter)
        self.pressure_sample_ratio = pressure_sample_ratio

    def write(self, prop_name, file_name, unit=None):
        save_x_tp(
            self.get_prop(prop_name, unit),
            self.calculator.temperature_array.to(units.kelvin).magnitude,
            self.calculator.pressure_array.to(units.GPa).magnitude,
            self.calculator.pressure_array.to(units.GPa).magnitude[0::self.pressure_sample_ratio],
            self.get_output_file_path(file_name)
        )
