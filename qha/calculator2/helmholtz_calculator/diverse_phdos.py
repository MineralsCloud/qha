import numpy
from lazy_property import LazyProperty

from qha.utils.readers import read_input
from qha.utils.units import QHAUnits

from .abstract import HelmholtzFreeEnergyCalculator
from .configuration import StructureConfiguration

from qha.calculator2.utils import is_all_same

import qha.multi_configurations.different_phonon_dos as different_phonon_dos

# TODO: move to other places

units = QHAUnits()

class DiversePhDOSHolmholtzFreeEnergyCalculator(HelmholtzFreeEnergyCalculator):
    def __init__(self, settings):
        super().__init__(settings)
        self.configurations = []
        self._degeneracies = self.settings['input'].values()
    
    def read_input(self):
        self.configurations = list(
            StructureConfiguration(*read_input(file_name))
            for file_name in self.settings['input'].keys()
        )

    def validate(self):
        super().validate()
        for configuration in self.configurations:
            configuration.validate()
    
    def validate_configurations_has_same_number_of_volumes(self):
        if not is_all_same(len(conf.dataset) for conf in self.configurations):
            raise RuntimeError('Not all configurations have the same number of volumes')

    def validate_configurations_has_same_formula_unit_number(self):
        if not is_all_same(conf.formulat_unit_number for conf in self.configurations):
            raise RuntimeError('Not all configurations have the same number of volumes')


    def calculate_helmholtz_free_energy(self):
        # We grep all the arguments once since they are being invoked for thousands of times, and will be an overhead.
        self._helmholtz_free_energies = numpy.array([ 
            different_phonon_dos.PartitionFunction(
                temperature,
                self.degeneracies.magnitude,
                self.all_q_weights,
                self.all_static_energies,
                self.all_volumes,
                self.all_frequencies,
                self.settings['static_only']
            ).get_free_energies()
            for temperature in self.get_temperature_array().magnitude
        ])
    
    def get_calibration_target_configuration(self):
        return self.configurations[0]
    
    @property
    def degeneracies(self):
        return self._degeneracies

    @LazyProperty
    @units.wraps(units.bohr**3, None)
    def volume_array(self):
        return numpy.array([
            pressure_data.volume for pressure_data
            in self.get_calibration_target_configuration().dataset
        ])

    def get_all_from_configurations(self, key: callable):
        return numpy.array([key(conf) for conf in self.configurations])
    
    @LazyProperty
    def all_q_weights(self):
        return self.get_all_from_configurations(lambda data: data.q_weights)
    
    def get_all_from_pressures_from_configurations(self, key: callable):
        return self.get_all_from_configurations(lambda conf: [
            key(pressure_data) for pressure_data in conf.dataset
        ])
    
    @LazyProperty
    @units.wraps(units.bohr**3, None)
    def all_volumes(self):
        return self.get_all_from_pressures_from_configurations(
            lambda data: data.volume
        )

    @LazyProperty
    @units.wraps(units.Ryd, None)
    def all_static_energies(self):
        return self.get_all_from_pressures_from_configurations(
            lambda data: data.static_energies
        )

    @LazyProperty
    @units.wraps(units.Hz, None)
    def all_frequencies(self):
        return self.get_all_from_pressures_from_configurations(
            lambda data: data.frequencies
        )
    
    @LazyProperty
    def formula_unit_number(self):
        return self.get_calibration_target_configuration().formula_unit_number