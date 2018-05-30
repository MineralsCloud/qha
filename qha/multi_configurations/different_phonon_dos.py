#!/usr/bin/env python3
"""
.. module different_phonon_dos
   :platform: Unix, Windows, Mac, Linux
   :synopsis:
.. moduleauthor:: Tian Qin <qinxx197@umn.edu>
.. moduleauthor:: Qi Zhang <qz2280@columbia.edu>
"""

from typing import Optional

import numpy as np
from lazy_property import LazyProperty
from scipy.constants import physical_constants as pc
from scipy.special import logsumexp

import qha.settings
from qha.single_configuration import free_energy
from qha.tools import calibrate_energy_on_reference
from qha.type_aliases import Array4D, Scalar, Vector, Matrix

# ===================== What can be exported? =====================
__all__ = ['PartitionFunction']

K = {'ha': pc['Boltzmann constant in eV/K'][0] / pc['Hartree energy in eV'][0],
     'ry': pc['Boltzmann constant in eV/K'][0] / pc['Rydberg constant times hc in eV'][0],
     'ev': pc['Boltzmann constant in eV/K'][0],
     'SI': pc['Boltzmann constant'][0]}[qha.settings.energy_unit]


class PartitionFunction:
    def __init__(self, temperature: Scalar, degeneracies: Vector, q_weights: Matrix, static_energies: Matrix,
                 volumes: Matrix, frequencies: Array4D, static_only: Optional[bool] = False,
                 precision: Optional[int] = 500, order: Optional[int] = 3):
        if not np.all(np.greater_equal(degeneracies, 0)):
            raise ValueError('Degeneracies should all be greater equal than 0!')
        if not np.all(np.greater_equal(
                q_weights, 0)):  # Weights should all be greater equal than 0, otherwise sum will be wrong.
            raise ValueError('Weights should all be greater equal than 0!')

        self.frequencies = np.array(frequencies)
        if self.frequencies.ndim != 4:
            raise ValueError("*frequencies* must be a four-dimensional array!")

        self.static_energies = np.array(static_energies)
        if self.static_energies.ndim != 2:
            raise ValueError("*static_energies* must be a two-dimensional array!")

        if temperature < 1e-1:
            self.temperature = 1
        else:
            self.temperature = temperature
        self.degeneracies = np.array(degeneracies)
        self.q_weights = np.array(q_weights)
        self._scaled_q_weights = self.q_weights / np.sum(q_weights)
        self.volumes = volumes
        self.static_only = static_only
        self.precision = int(precision)
        self.order = int(order)

    @LazyProperty
    def helmoholtz_configs(self):
        num_configs, _ = self.volumes.shape
        f = [free_energy(self.temperature, self.q_weights[i], self.static_energies[i], self.frequencies[i],
                         self.static_only) for i in
             range(num_configs)]
        return np.array(f)

    @LazyProperty
    def helmholtz_at_ref_v(self):
        return calibrate_energy_on_reference(self.volumes, self.helmoholtz_configs, self.order)

    @LazyProperty
    def partition_from_helmholtz(self):
        try:
            import bigfloat
        except ImportError:
            raise ImportError(
                "You need to install ``bigfloat`` package to use {0} object!".format(self.__class__.__name__))

        with bigfloat.precision(self.precision):
            return np.array([bigfloat.exp(d) for d in  # shape = (# of volumes for each configuration, 1)
                             logsumexp(-self.helmholtz_at_ref_v.T / (K * self.temperature), axis=1,
                                       b=self.degeneracies)])

    @LazyProperty
    def derive_free_energy(self):
        try:
            import bigfloat
        except ImportError:
            raise ImportError(
                "You need to install ``bigfloat`` package to use {0} object!".format(self.__class__.__name__))

        with bigfloat.precision(self.precision):
            log_z = np.array([bigfloat.log(d) for d in self.partition_from_helmholtz], dtype=float)
        return -K * self.temperature * log_z
