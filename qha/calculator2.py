import numpy

from typing import Dict, Any, Optional
from qha.units import QHAUnits
from qha.type_aliases import Vector

import qha.multi_configurations.different_phonon_dos as different_phonon_dos
import qha.multi_configurations.same_phonon_dos as same_phonon_dos
import qha.tools
from qha.grid_interpolation import RefineGrid
from qha.out import save_to_output
from qha.readers import read_input
from qha.single_configuration import free_energy
from qha.thermodynamics import *
from qha.v2p import v2p

import textwrap

units = QHAUnits()

__all__ = [
    'BasicTemperatureVolumeFieldCalculator',
    'SamePhononDOSTemperatureVolumeFieldCalculator',
    'DifferentPhononDOSTemperatureVolumeFieldCalculator',
    'PerFormulaUnit',
    'VolumeToPressureFieldAdapter',
]

class BasicTemperatureVolumeFieldCalculator:

    def __init__(self, user_settings: Dict[str, Any]):
        # TODO: keys and required keys

        self.allowed_keys = ('same_phonon_dos', 'input', 'volume_energies',
                'calculate', 'static_only', 'energy_unit',
                'T_MIN', 'NT', 'DT', 'DT_SAMPLE',
                'P_MIN', 'NTV', 'DELTA_P', 'DELTA_P_SAMPLE',
                'calculate', 'volume_ratio', 'order', 'p_min_modifier',
                'T4FV', 'output_directory', 'plot_results', 'high_verbosity', 'qha_output')

        self._settings = None

        self._formula_unit_number = None
        self._volumes = None
        self._static_energies = None
        self._frequencies = None
        self._q_weights = None

        self._coarse_helmholtz_free_energy = None

        self._temperature_array = None
        self._desired_pressures = None

        self._fine_volumes = None
        self._fine_pressures = None
        self._fine_helmholtz_free_energy = None
        self._fine_thermodynamic_potentials = None

        self._v_ratio = None

        # TODO: Warning: update setting should not be here.

        self.update_settings(user_settings)
        self.prepare_temperature_array()
        self.prepare_desired_pressures()




    @property
    def formula_unit_number(self):
        return self._formula_unit_number
    
    def update_settings(self, user_settings: Dict[str, Any]):
        self._settings = dict()
        for key in self.allowed_keys:
            try:
                self._settings.update({key: user_settings[key]})
            except KeyError:
                continue  # If a key is not set in user settings, use the default.

    @property
    def settings(self): return self._settings

    def validate_settings(self): pass

    def read_input(self):
        try:
            formula_unit_number, \
            volumes, \
            static_energies, \
            frequencies, \
            q_weights = read_input(self.settings['input'])
        except KeyError:
            raise KeyError("The 'input' option must be given in your settings!")

        if not qha.tools.is_monotonic_decreasing(volumes):
            raise RuntimeError("Check the input file to make sure the volume decreases!")

        self._formula_unit_number: int = formula_unit_number
        self._volumes = volumes
        self._static_energies = static_energies
        self._frequencies = frequencies
        self._q_weights = q_weights
        
    def calculate(self):
        #self._settings = dict()
        #self.update_settings(user_settings)
        self._coarse_helmholtz_free_energy = numpy.array(list(self.calculate_free_energy()))
        self.refine_grid()
        self.calculate_thermodynamic_potentials()
    
    def prepare_temperature_array(self):
        minimum_temperature = self.settings['T_MIN']
        if minimum_temperature < 0:
            raise ValueError("Minimum temperature should be no less than 0!")
        # Normally, the last 2 temperature points in Cp are not accurate.
        # Here 4 more points are added for calculation, but they will be removed at the output files.
        self._temperature_array = qha.tools.arange(minimum_temperature, self.settings['NT'] + 4, self.settings['DT'])

    def prepare_desired_pressures(self):
        self._desired_pressures = units.Quantity(qha.tools.arange(
            self.settings['P_MIN'],
            self.settings['NTV'],
            self.settings['DELTA_P']
        ), units.GPa).to(units.Ryd / units.Bohr**3).magnitude

    def calculate_free_energy(self):
        for temperature in self._temperature_array:
            yield free_energy(
                temperature,
                self._q_weights,
                self._static_energies,
                self._frequencies,
                self.settings['static_only']
            )

    def calculate_thermodynamic_potentials(self):
        self._fine_thermodynamic_potentials =\
            thermodynamic_potentials(
                self._temperature_array,
                self._fine_volumes,
                self._fine_helmholtz_free_energy,
                self._fine_pressures
            )

    def refine_grid(self):
        p_min          = self.settings['P_MIN']
        p_min_modifier = self.settings['p_min_modifier']
        ntv            = self.settings['NTV']
        order          = self.settings['order']
        ratio          = self.settings['volume_ratio'] if 'volume_ratio' in self.settings.keys() else None

        refiner = RefineGrid(p_min - p_min_modifier, ntv, order=order)

        self._fine_volumes, \
        self._fine_helmholtz_free_energy, \
        self._v_ratio = refiner.refine_grid(
            self.get_coarse_volumes().magnitude, # TODO: ???
            self._coarse_helmholtz_free_energy,
            ratio=ratio)
        self._fine_pressures = pressure_tv(
            self._fine_volumes,
            self._fine_helmholtz_free_energy)

    def check_desired_pressure_status(self) -> None:
        # TODO: Maybe should in adapter
        d = self.settings
        p_tv_gpa = self.get_pressures().to(units.GPa).magnitude
        desired_pressures_gpa = self.get_desired_pressures().to(units.GPa).magnitude

        # TODO: Should not write output here
        if d['high_verbosity']:
            save_to_output(d['qha_output'], "The pressure range can be dealt with: [{0:6.2f} to {1:6.2f}] GPa".format(
                p_tv_gpa[:, 0].max(),
                p_tv_gpa[:, -1].min()
            ))
        
        if p_tv_gpa[:, -1].min() < desired_pressures_gpa.max():
            ntv_max = int((p_tv_gpa[:, -1].min() - desired_pressures_gpa.min()) / d['DELTA_P'])

            save_to_output(d['qha_output'], textwrap.dedent("""\
                           !!!ATTENTION!!!
                           
                           DESIRED PRESSURE is too high (NTV is too large)!
                           QHA results might not be right!
                           Please reduce the NTV accordingly, for example, try to set NTV < {:4d}.
                           """.format(ntv_max)))

            raise ValueError("DESIRED PRESSURE is too high (NTV is too large), qha results might not be right!")

    def find_negative_frequencies(self) -> Optional[Vector]:
        """
        The indices of negative frequencies are indicated.

        :return:
        """
        if self._frequencies is None:
            print("Please invoke ``read_input`` method first!")  # ``None`` is returned
        else:
            locations = numpy.transpose(numpy.where(self._frequencies < 0))
            if locations.size == 0:
                return None

            return locations
    
    @units.wraps(units.Hz, None)
    def get_frequencies(self):
        return self._frequencies

    @units.wraps(units.Ryd / units.Bohr ** 3, None)
    def get_pressures(self):
        return self._fine_pressures
    @units.wraps(units.Bohr**3, None)
    def get_volumes(self):
        return self._fine_volumes
    @units.wraps(units.Ryd / units.Bohr ** 3, None)
    def get_desired_pressures(self):
        return self._desired_pressures
    @units.wraps(units.kelvin, None)
    def get_temperature_array(self):
        return self._temperature_array
    
    @units.wraps(units.Ryd, None)
    def get_coarse_helmholtz_free_energy(self):
        return self._coarse_helmholtz_free_energy
    @units.wraps(units.Bohr**3, None)
    def get_coarse_volumes(self):
        return self._volumes

    @units.wraps(units.Ryd, None)
    def get_helmholtz_free_energy(self):
        return self._fine_helmholtz_free_energy

    @units.wraps(units.Ryd, None)
    def get_gibbs_free_energy(self):
        return self._fine_thermodynamic_potentials['G']
    @units.wraps(units.Ryd, None)
    def get_internal_energy(self):
        return self._fine_thermodynamic_potentials['U']
    @units.wraps(units.Ryd, None)
    def get_entropy(self):
        return self._fine_thermodynamic_potentials['H']
    
    @units.wraps(units.Ryd / units.Bohr ** 3, None)
    def get_isothermal_bulk_modulus(self):
        return isothermal_bulk_modulus(
            self._fine_volumes,
            self._fine_pressures)
 
    @units.wraps(units.Ryd / units.kelvin, None)
    def get_volume_specific_heat_capacity(self):
        return volume_specific_heat_capacity(
            self._temperature_array,
            self.get_internal_energy().magnitude)

    @units.wraps(units.kelvin, None)
    def get_temperature_sample_array(self):
        return self._temperature_array[0::int(self.settings['DT_SAMPLE'] / self.settings['DT'])]

    @units.wraps(units.Ryd / units.Bohr**3, None)
    def get_pressure_sample_array(self):
        # TODO: / ?
        return self.get_desired_pressures().magnitude[0::int(self.settings['DELTA_P_SAMPLE'] / self.settings['DELTA_P'])]

class VolumeToPressureFieldAdapter:
    def __init__(self, calculator: BasicTemperatureVolumeFieldCalculator):
        self.calculator = calculator
        self._settings = self.calculator.settings

    @property
    def settings(self): return self.calculator.settings

    @units.wraps(units.Ryd / units.Bohr ** 3, None)
    def get_pressures(self):
        return self.calculator.get_pressures().magnitude
    @units.wraps(units.Bohr ** 3, None)
    def get_volumes(self):
        return volume_tp(
            self.calculator.get_volumes().magnitude,
            self.get_desired_pressures().magnitude,
            self.get_pressures().magnitude
        )
        #return self.calculator.get_volumes().magnitude
    @units.wraps(units.Ryd / units.Bohr ** 3, None)
    def get_desired_pressures(self):
        return self.calculator._desired_pressures
    @units.wraps(units.kelvin, None)
    def get_temperature_array(self):
        return self.calculator.get_temperature_array().magnitude
    
    def __convert_to_pressure_field(self, volume_field):
        print(volume_field)
        return v2p(
            volume_field,
            self.get_pressures().magnitude,
            self.get_desired_pressures().magnitude
        )
    
    @units.wraps(units.Ryd, None)
    def get_helmholtz_free_energy(self):
        return self.__convert_to_pressure_field(
            self.calculator.get_helmholtz_free_energy().magnitude
        )

    @units.wraps(units.Ryd, None)
    def get_gibbs_free_energy(self):
        return self.__convert_to_pressure_field(
            self.calculator.get_gibbs_free_energy().magnitude
        )
    @units.wraps(units.Ryd, None)
    def get_internal_energy(self):
        return self.__convert_to_pressure_field(
            self.calculator.get_internal_energy().magnitude
        )
    @units.wraps(units.Ryd, None)
    def get_entropy(self):
        return self.__convert_to_pressure_field(
            self.calculator.get_entropy().magnitude
        )

    @units.wraps(units.Ryd / units.Bohr ** 2, None)
    def get_isothermal_bulk_modulus(self):
        return self.__convert_to_pressure_field(
            self.calculator.get_isothermal_bulk_modulus().magnitude
        )
    @units.wraps(units.Ryd / units.Bohr ** 2, None)
    def get_adiabatic_bulk_modulus(self):
        return adiabatic_bulk_modulus(
            self.get_isothermal_bulk_modulus().magnitude,
            self.get_thermal_expansion_coefficient().magnitude,
            self.get_gruneisen_parameter().magnitude,
            self.get_temperature_array().magnitude
        )
 
    @units.wraps(units.Ryd / units.kelvin, None)
    def get_volume_specific_heat_capacity(self):
        return self.__convert_to_pressure_field(
            self.calculator.get_volume_specific_heat_capacity().magnitude
        )
    @units.wraps(units.Ryd / units.kelvin, None)
    def get_pressure_specific_heat_capacity(self):
        return pressure_specific_heat_capacity(
            self.get_volume_specific_heat_capacity().magnitude,
            self.get_thermal_expansion_coefficient().magnitude,
            self.get_gruneisen_parameter().magnitude,
            self.get_temperature_array().magnitude
        )
    @units.wraps(units.dimensionless, None)
    def get_gruneisen_parameter(self):
        return gruneisen_parameter(
            self.get_volumes().magnitude,
            self.get_isothermal_bulk_modulus().magnitude,
            self.get_thermal_expansion_coefficient().magnitude,
            self.calculator.get_volume_specific_heat_capacity().magnitude
        )
    @units.wraps(units.kelvin ** -1, None)
    def get_thermal_expansion_coefficient(self):
        return thermal_expansion_coefficient(
            self.get_temperature_array().magnitude,
            self.get_volumes().magnitude
        )
    @units.wraps(units.dimensionless, None)
    def get_isothermal_bulk_modulus_pressure_derivative(self):
        return bulk_modulus_derivative(
            self.get_desired_pressures().magnitude,
            self.get_isothermal_bulk_modulus().magnitude
        )

class PerFormulaUnit:
    def __init__(self, item):
        self.item = item
    def __getattr__(self, prop):
        item_attr = getattr(self.item, prop)
        if callable(item_attr):
            def wrapper(*argv, **kwargs):
                return item_attr(*argv, **kwargs) / self.item._formula_unit_number
            return wrapper
        else:
            return item_attr / self.item._formula_unit_number

class DifferentPhononDOSTemperatureVolumeFieldCalculator(BasicTemperatureVolumeFieldCalculator):
    def __init__(self, user_settings: Dict[str, Any]):
        super().__init__(user_settings)
        self._degeneracies = None

    def get_degeneracies(self):
        return self._degeneracies

    def read_input(self):
        self._degeneracies = tuple(self.settings['input'].values())
        input_data_files = tuple(self.settings['input'].keys())

        formula_unit_numbers = []
        volumes = []
        static_energies = []
        frequencies = []
        q_weights = []

        for inp in input_data_files:
            nm_tmp, volumes_tmp, static_energies_tmp, freq_tmp, weights_tmp = read_input(inp)

            if not qha.tools.is_monotonic_decreasing(volumes_tmp):
                # TODO: Clean this sentence
                save_to_output(self.settings['qha_output'], "Check the input file to make sure the volume decreases")
                raise ValueError("Check the input file to make sure the volumes are monotonic decreasing!")

            formula_unit_numbers.append(nm_tmp)
            volumes.append(volumes_tmp)
            static_energies.append(static_energies_tmp)
            frequencies.append(freq_tmp)
            q_weights.append(weights_tmp)

        formula_unit_numbers = numpy.array(formula_unit_numbers)
        volumes = numpy.array(volumes)
        static_energies = numpy.array(static_energies)
        frequencies = numpy.array(frequencies)
        q_weights = numpy.array(q_weights)

        if not len(set(formula_unit_numbers)) == 1:
            raise RuntimeError("All the formula unit number in all inputs should be the same!")

        if len(volumes.shape) == 1:
            raise RuntimeError("All configurations should have same number of volumes!")

        self._formula_unit_number = formula_unit_numbers[0]  # Choose any of them since they are all the same
        self._static_energies = static_energies
        self._frequencies = frequencies
        self._q_weights = q_weights

        self._volumes = volumes
    
    @units.wraps(units.Bohr ** 3, None)
    def get_coarse_volumes(self):
        return self._volumes[0]
    #@property
    #def volumes(self):
        # TODO: This is a bad style, they should be consistent
        #return self._volumes[0]


    def calculate_free_energy(self):
        # We grep all the arguments once since they are being invoked for thousands of times, and will be an overhead.
        for temperature in self.get_temperature_array().magnitude:
            yield different_phonon_dos.PartitionFunction(
                temperature,
                self._degeneracies,
                self._q_weights,
                self._static_energies,
                self._volumes, # ??
                self._frequencies,
                self._settings['static_only']
            ).get_free_energies()

class SamePhononDOSTemperatureVolumeFieldCalculator(DifferentPhononDOSTemperatureVolumeFieldCalculator):
    def calculate_free_energy(self):
        for temperature in self.get_temperature_array().magnitude:
            yield same_phonon_dos.FreeEnergy(
                temperature,
                self._degeneracies,
                self._q_weights[0],
                self._static_energies,
                self._volumes[0], # TODO: !!!???
                self._frequencies[0],
                self._settings['static_only'],
                self.settings['order']
            ).get_free_energies()

