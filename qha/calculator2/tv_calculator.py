import numpy
from lazy_property import LazyProperty

from typing import Dict, Any, Optional
from qha.type_aliases import Vector

from qha.utils.units import QHAUnits
from qha.utils.out import save_to_output

import qha.tools
from qha.grid_interpolation import RefineGrid
from qha.single_configuration import free_energy
from qha.thermodynamics import *
from qha.v2p import v2p
from qha.calculator2.helmholtz_calculator import *

from .tp_adapter import TemperaturePressureFieldAdapter

__all__ = [
    'TemperatureVolumeFieldCalculator',
]

units = QHAUnits()

class TemperatureVolumeFieldCalculator:

    __allowed_keys = [
        'same_phonon_dos', 'input', 'volume_energies',
        'calculate', 'static_only', 'energy_unit',
        'T_MIN', 'NT', 'DT', 'DT_SAMPLE',
        'P_MIN', 'NTV', 'DELTA_P', 'DELTA_P_SAMPLE',
        'calculate', 'volume_ratio', 'order', 'p_min_modifier',
        'T4FV', 'output_directory', 'plot_results', 'high_verbosity', 'qha_output'
    ]

    def __init__(self, settings: Dict[str, Any]):
        self._settings = dict()
        for key in self.__allowed_keys:
            if key in settings:
                self._settings.update({key: settings[key]})
            # TODO: Use default when a key is not present

        self._helmholtz_free_energy_calculator: HelmholtzFreeEnergyCalculator = None

        self._helmholtz_free_energies = None
        self._thermodynamic_potentials = None
        self.v_ratio = None

        self._temperature_pressure_adapter = None

        self.make_helmholtz_free_energy_calculator()
        self.make_temperature_pressure_adapter()

    @property
    def formula_unit_number(self):
        return self.helmholtz_free_energy_calculator.formula_unit_number

    @property
    def settings(self):
        return self._settings
    
    @property
    def helmholtz_free_energy_calculator(self):
        return self._helmholtz_free_energy_calculator
    
    @property
    def temperature_pressure_field_adapter(self):
        return self._temperature_pressure_field_adapter
    
    def make_helmholtz_free_energy_calculator(self):
        user_input = self.settings['input']
        if isinstance(user_input, str):
            self._helmholtz_free_energy_calculator = SingleConfigurationHelmholtzFreeEnergyCalculator(self.settings)
        elif isinstance(user_input, dict):
            if self.settings['same_phonon_dos']:
                self._helmholtz_free_energy_calculator = IdenticalPhDOSHolmholtzFreeEnergyCalculator(self.settings)
            else:
                self._helmholtz_free_energy_calculator = DiversePhDOSHolmholtzFreeEnergyCalculator(self.settings)
        else:
            raise ValueError("The 'input' in your settings in not recognized! It must be a dictionary or a list!")
    
    def make_temperature_pressure_adapter(self):
        self._temperature_pressure_field_adapter = TemperaturePressureFieldAdapter(self)

    def validate(self):
        pass

    def calculate(self):
        self.helmholtz_free_energy_calculator.read_input()
        self.helmholtz_free_energy_calculator.validate()
        self.helmholtz_free_energy_calculator.calculate()
        self.refine_grid()
        self.calculate_thermodynamic_potentials()
        self.temperature_pressure_field_adapter.validate()
    
    def calculate_thermodynamic_potentials(self):
        self._thermodynamic_potentials = \
            thermodynamic_potentials(
                self.temperature_array.magnitude,
                self.volume_array.magnitude,
                self.helmholtz_free_energies.magnitude,
                self.pressures.magnitude
            )
    
    def refine_grid(self):
        p_min          = self.settings['P_MIN']
        p_min_modifier = self.settings['p_min_modifier']
        ntv            = self.settings['NTV']
        order          = self.settings['order']

        ratio          = self.settings.get('volume_ratio')

        refiner = RefineGrid(p_min - p_min_modifier, ntv, order=order)

        self._volume_array, \
        self._helmholtz_free_energies, \
        self.v_ratio = refiner.refine_grid(
            self.helmholtz_free_energy_calculator.volume_array.magnitude,
            self.helmholtz_free_energy_calculator.helmholtz_free_energies.magnitude,
            ratio=ratio
        )

    @LazyProperty
    @units.wraps(units.kelvin, None)
    def temperature_array(self):
        return self.helmholtz_free_energy_calculator.temperature_array.magnitude
    
    @property
    @units.wraps(units.Bohr**3, None)
    def volume_array(self):
        return self._volume_array
    
    @property
    @units.wraps(units.Ryd, None)
    def helmholtz_free_energies(self):
        return self._helmholtz_free_energies

    @LazyProperty
    @units.wraps(units.Ryd, None)
    def gibbs_free_energies(self):
        return self._thermodynamic_potentials['G']

    @LazyProperty
    @units.wraps(units.Ryd, None)
    def internal_energies(self):
        return self._thermodynamic_potentials['U']

    @LazyProperty
    @units.wraps(units.Ryd, None)
    def entropies(self):
        return self._thermodynamic_potentials['H']

    @LazyProperty
    @units.wraps(units.Ryd / units.kelvin, None)
    def volume_specific_heat_capacities(self):
        return volume_specific_heat_capacity(
            self.temperature_array.magnitude,
            self.internal_energies.magnitude
        )
    
    @LazyProperty
    @units.wraps(units.Ryd / units.Bohr ** 3, None)
    def isothermal_bulk_moduli(self):
        return isothermal_bulk_modulus(
            self.volume_array.magnitude,
            self.pressures.magnitude
        )

    @LazyProperty
    @units.wraps(units.Ryd / units.Bohr ** 3, None)
    def pressures(self):
        return pressure_tv(
            self.volume_array.magnitude,
            self.helmholtz_free_energies.magnitude
        )
