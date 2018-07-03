import numpy
from lazy_property import LazyProperty

from qha.utils.readers import read_input
from qha.single_configuration import free_energy
from qha.utils.units import QHAUnits

from .abstract import HelmholtzFreeEnergyCalculator
from .configuration import StructureConfiguration

units = QHAUnits()

class SingleConfigurationHelmholtzFreeEnergyCalculator(HelmholtzFreeEnergyCalculator):
    def __init__(self, settings):
        super().__init__(settings)
        self.configuration = None
    
    def read_input(self):
        self.configuration = StructureConfiguration(
            *read_input(self.settings['input'])
        )
    
    def validate(self):
        super().validate()
        self.configuration.validate()

    def calculate_helmholtz_free_energy(self):
        self._helmholtz_free_energies = numpy.array([
            free_energy(
                temperature,
                self.configuration.q_weights,
                self.configuration.static_energies.magnitude,
                self.configuration.frequencies.magnitude,
                self.settings['static_only'])
            for temperature in self.temperature_array.magnitude
        ])
    
    @LazyProperty
    @units.wraps(units.bohr**3, None)
    def volume_array(self):
        return numpy.array([
            pressure_data.volume for pressure_data in self.configuration.dataset
        ])
    
    @LazyProperty
    def formula_unit_number(self):
        return self.configuration.formula_unit_number