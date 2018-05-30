#!/usr/bin/env python3
"""
.. module same_phonon_dos
   :platform: Unix, Windows, Mac, Linux
   :synopsis:
.. moduleauthor:: Qi Zhang <qz2280@columbia.edu>
"""

from typing import Optional

import numpy as np
from lazy_property import LazyProperty
from scipy.constants import physical_constants as pc
from scipy.special import logsumexp

import qha.settings
from qha.statmech import ho_free_energy, log_subsystem_partition_function
from qha.tools import calibrate_energy_on_reference
from qha.type_aliases import Array3D, Scalar, Vector, Matrix

# ===================== What can be exported? =====================
__all__ = ['PartitionFunction', 'FreeEnergy']

K = {'ha': pc['Boltzmann constant in eV/K'][0] / pc['Hartree energy in eV'][0],
     'ry': pc['Boltzmann constant in eV/K'][0] / pc['Rydberg constant times hc in eV'][0],
     'ev': pc['Boltzmann constant in eV/K'][0],
     'SI': pc['Boltzmann constant'][0]}[qha.settings.energy_unit]


class PartitionFunction:
    def __init__(self, temperature: Scalar, degeneracies: Vector, q_weights: Vector, static_energies: Matrix,
                 frequencies: Array3D, precision: Optional[int] = 500):

        if not np.all(np.greater_equal(degeneracies, 0)):
            raise ValueError('Degeneracies should all be integers greater equal than 0!')
        if not np.all(np.greater_equal(q_weights,
                                       0)):  # Weights should all be greater equal than 0, otherwise sum will be wrong.
            raise ValueError('Weights should all be greater equal than 0!')

        self.frequencies = np.array(frequencies)
        if self.frequencies.ndim != 3:
            raise ValueError("*frequencies* must be a three-dimensional array!")

        if temperature < 1e-6:
            self.temperature = 1e-6
        else:
            self.temperature = temperature
        self.static_energies = np.array(static_energies)
        self.degeneracies = np.array(degeneracies)
        self.q_weights = np.array(q_weights)
        self._scaled_q_weights = self.q_weights / np.sum(q_weights)
        self.precision = int(precision)

    @LazyProperty
    def static_part(self) -> Vector:
        try:
            import bigfloat
        except ImportError:
            raise ImportError(
                "You need to install ``bigfloat`` package to use {0} object!".format(self.__class__.__name__))

        with bigfloat.precision(self.precision):
            return np.array([bigfloat.exp(d) for d in  # shape = (# of volumes for each configuration, 1)
                             logsumexp(-self.static_energies / (K * self.temperature), axis=1, b=self.degeneracies)])

    @LazyProperty
    def harmonic_part(self) -> Vector:
        log_product_modes: Matrix = np.sum(
            log_subsystem_partition_function(self.temperature, self.frequencies), axis=2, dtype=float)
        return np.exp(np.dot(log_product_modes, self._scaled_q_weights))  # (vol, 1)

    @LazyProperty
    def total(self) -> Vector:
        return np.multiply(self.static_part, self.harmonic_part)  # (vol, 1), product element-wise

    def derive_free_energy(self):
        try:
            import bigfloat
        except ImportError:
            raise ImportError(
                "You need to install ``bigfloat`` package to use {0} object!".format(self.__class__.__name__))

        with bigfloat.precision(self.precision):
            log_z = np.array([bigfloat.log(d) for d in self.total], dtype=float)
        return -K * self.temperature * log_z


class FreeEnergy:
    def __init__(self, temperature: Scalar, degeneracies: Vector, q_weights: Vector, static_energies: Matrix,
                 volumes: Matrix, frequencies: Array3D, static_only: Optional[bool] = False, order: Optional[int] = 3):
        if not np.all(np.greater_equal(degeneracies, 0)):
            raise ValueError('Degeneracies should all be integers greater equal than 0!')
        if not np.all(np.greater_equal(q_weights,
                                       0)):  # Weights should all be greater equal than 0, otherwise sum will be wrong.
            raise ValueError('Weights should all be greater equal than 0!')

        self.frequencies = np.array(frequencies)
        if self.frequencies.ndim != 3:
            raise ValueError("*frequencies* must be a three-dimensional array!")

        if temperature < 1e-6:
            self.temperature = 1e-6
        else:
            self.temperature = temperature
        self.static_energies = np.array(static_energies)
        self.volumes = np.array(volumes)
        self.degeneracies = np.array(degeneracies)
        self.q_weights = np.array(q_weights)
        self._scaled_q_weights = self.q_weights / np.sum(q_weights)
        self.static_only = static_only
        self.order = order

    @LazyProperty
    def static_energy_at_ref_v(self):
        return calibrate_energy_on_reference(self.volumes, self.static_energies, self.order)

    @LazyProperty
    def static_part(self) -> Vector:
        kt: float = K * self.temperature  # k_B T
        inside_exp: Matrix = -self.static_energy_at_ref_v.T / kt  # exp( E_n(V) / k_B / T )
        return -kt * logsumexp(inside_exp, axis=1, b=self.degeneracies)

    @LazyProperty
    def harmonic_part(self) -> Vector:
        sum_modes = np.sum(ho_free_energy(self.temperature, self.frequencies), axis=2)
        return np.dot(sum_modes, self._scaled_q_weights)

    @LazyProperty
    def total(self) -> Vector:
        return self.static_part + self.harmonic_part

    @LazyProperty
    def derive_free_energy(self):
        if self.static_only:
            return self.static_part

        return self.total
