#!/usr/bin/env python3
"""
:mod:`mod` -- title
========================================

.. module mod
   :platform: Unix, Windows, Mac, Linux
   :synopsis:
.. moduleauthor:: Tian Qin <qinxx197@umn.edu>
.. moduleauthor:: Qi Zhang <qz2280@columbia.edu>
"""

import numpy as np
from lazy_property import LazyProperty
from scipy.constants import Boltzmann
from scipy.special import logsumexp

import qha.settings
from qha.bmf import bmf
from qha.grid_interpolation import calc_eulerian_strain
from qha.single_configuration import free_energy
from qha.type_aliases import Array4D, Scalar, Vector, Matrix

# ===================== What can be exported? =====================
__all__ = ['PartitionFunction']

K = {
    'ha': 8.6173303e-5 / 13.605698066 / 2,
    'ry': 8.6173303e-5 / 13.605698066,
    'ev': 8.6173303e-5,
    'SI': Boltzmann
}[qha.settings.energy_unit]


class PartitionFunction:
    def __init__(self, temperature: Scalar, static_energies: Matrix, degeneracies: Vector, q_weights: Matrix,
                 frequencies: Array4D, volumes: Matrix, static_only: bool, precision: int = 500):
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

    @LazyProperty
    def helmoholtz_configs(self):
        num_configs, _ = self.volumes.shape
        f = [free_energy(self.temperature, self.q_weights[i], self.static_energies[i], self.frequencies[i],
                         self.static_only) for i in
             range(num_configs)]
        return np.array(f)

    @LazyProperty
    def helmholtz_at_ref_v(self):
        num_configs, num_volumes = self.volumes.shape
        # Make the volumes of config 1 as a reference volume
        # The helmoholtz energies of other configs will recalibrate to these certain volumes.
        helmholtz_fitted = np.empty(self.volumes.shape)
        for i in range(num_configs):
            # strains, finer_volumes[i, :] = interpolate_volumes(self.volumes[i], self.__ntv, 1.05)
            eulerian_strain = calc_eulerian_strain(self.volumes[i][0], self.volumes[i])
            strains = calc_eulerian_strain(self.volumes[i][0], self.volumes[0])
            helmholtz_fitted[i, :] = bmf(eulerian_strain, self.helmoholtz_configs[i], strains)  # TODO add 'order' here
        return helmholtz_fitted

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
