#!/usr/bin/env python3

from typing import List

import numpy
from lazy_property import LazyProperty

from qha.utils.units import QHAUnits

units = QHAUnits()


class PressureSpecificData:
    def __init__(self, volume, static_energy, frequencies):
        self.volume = volume
        self.static_energy = static_energy
        self.frequencies = frequencies


class StructureConfiguration:
    def __init__(self, formula_unit_number, volumes, static_energies, frequencies, q_weights):
        self._formula_unit_number = formula_unit_number
        self._q_weights = q_weights

        self.dataset: List[PressureSpecificData] = sorted([
            PressureSpecificData(*v) for v in zip(volumes, static_energies, frequencies)
        ], key=lambda data: data.volume, reverse=True)

    def validate(self):
        self.validate_correct_num_of_frequencies()

    def validate_correct_num_of_frequencies(self):
        if not all(
                len(list(pressure_specific_data.frequencies)) == len(self.q_weights)
                for pressure_specific_data in self.dataset
        ):
            raise RuntimeError('Wrong number of frequencies')

    @property
    def formula_unit_number(self):
        return self._formula_unit_number

    @property
    def q_weights(self):
        return self._q_weights

    @LazyProperty
    @units.wraps(units.bohr ** 3, None)
    def volumes(self):
        return numpy.array([data.volume for data in self.dataset])

    @LazyProperty
    @units.wraps(units.bohr ** 3, None)
    def static_energies(self):
        return numpy.array([data.static_energy for data in self.dataset])

    @LazyProperty
    @units.wraps(units.Hz, None)
    def frequencies(self):
        return numpy.array([data.frequencies for data in self.dataset])
