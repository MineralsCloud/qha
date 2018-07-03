import numpy
from typing import List, Optional
from lazy_property import LazyProperty

import qha.tools
from qha.utils.units import QHAUnits
from qha.utils.readers import read_input
from qha.type_aliases import Vector

units = QHAUnits()

class HelmholtzFreeEnergyCalculator:
    def __init__(self, settings):
        self._helmholtz_free_energies = None
        self.settings = settings
        self.read_input()
    
    def find_negative_frequencies(self) -> Optional[Vector]:
        locations = numpy.transpose(numpy.where(self.frequencies.magnitude < 0))
        return locations if locations.size != 0 else None

    def read_input(self):
        raise NotImplementedError()

    def validate(self):
        self.validate_positive_temperature()

    def validate_positive_temperature(self):
        if numpy.any(numpy.sign(self.temperature_array.magnitude) < 0):
            raise RuntimeError('Working temperatures should be above zero.')

    def calculate(self):
        #self.read_input()
        # TODO: position of read_input
        self.calculate_helmholtz_free_energy()
        #print(self.helmholtz_free_energies_2)
        #print(self.helmholtz_free_energies)

    def calculate_helmholtz_free_energy(self):
        raise NotImplementedError()

    @property
    def formula_unit_number(self):
        return NotImplementedError()

    @LazyProperty
    @units.wraps(units.kelvin, None)
    def temperature_array(self):
        # Normally, the last 2 temperature points in Cp are not accurate.
        # Here 4 more points are added for calculation, but they will be removed at the output files.
        return qha.tools.arange(
            self.settings['T_MIN'],
            self.settings['NT'] + 4,
            self.settings['DT']
        )

    #@LazyProperty
    @property
    @units.wraps(units.Ryd, None)
    def helmholtz_free_energies(self):
        return self._helmholtz_free_energies