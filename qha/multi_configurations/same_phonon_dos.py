#!/usr/bin/env python3
"""
:mod:`mod` -- title
========================================

.. module mod
   :platform: Unix, Windows, Mac, Linux
   :synopsis:
.. moduleauthor:: Qi Zhang <qz2280@columbia.edu>
"""

import numpy as np
from lazy_property import LazyProperty
from scipy.constants import Boltzmann
from scipy.special import logsumexp

import qha.settings
from qha.statmech import ho_free_energy, log_subsystem_partition_function
from qha.type_aliases import Array3D, Scalar, Vector, Matrix

# ===================== What can be exported? =====================
__all__ = ['PartitionFunction', 'FreeEnergy']

K = {
    'ha': 8.6173303e-5 / 13.605698066 / 2,
    'ry': 8.6173303e-5 / 13.605698066,
    'ev': 8.6173303e-5,
    'SI': Boltzmann
}[qha.settings.energy_unit]


class PartitionFunction:
    def __init__(self, temperature: Scalar, static_energies: Matrix, degeneracies: Vector, q_weights: Vector,
                 frequencies: Array3D, precision: int = 500):

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
    def __init__(self, temperature: Scalar, static_energies: Matrix, degeneracies: Vector, q_weights: Vector,
                 frequencies: Array3D):
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

    @LazyProperty
    def static_part(self) -> Vector:
        kt: float = K * self.temperature  # k_B T
        inside_exp: Matrix = -self.static_energies / kt  # exp( E_n(V) / k_B / T )
        return -kt * logsumexp(inside_exp, axis=1, b=self.degeneracies)

    @LazyProperty
    def harmonic_part(self) -> Vector:
        sum_modes = np.sum(ho_free_energy(self.temperature, self.frequencies), axis=2)
        return np.dot(sum_modes, self._scaled_q_weights)

    @LazyProperty
    def total(self) -> Vector:
        return self.static_part + self.harmonic_part
