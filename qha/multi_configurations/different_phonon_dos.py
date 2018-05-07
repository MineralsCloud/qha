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
from qha.bmf import bmf_energy, birchmurnaghan_energy
from qha.grid_interpolation import interpolate_volumes, calc_eulerian_strain
from qha.single_configuration import free_energy
from qha.tools import _lagrange4
from qha.tools import vectorized_find_nearest
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
        self.__ntv = 400

    @LazyProperty
    def helmoholtz_configs(self):
        num_configs, _ = self.volumes.shape
        f = [free_energy(self.temperature, self.q_weights[i], self.static_energies[i], self.frequencies[i],
                         self.static_only) for i in
             range(num_configs)]
        return np.array(f)

    @LazyProperty
    def helmholtz_at_dense_v(self):
        num_configs, _ = self.volumes.shape
        # Make the volumes of config 1 as a reference volume
        # The helmoholtz energies of other configs will recalibrate to these certain volumes.
        helmholtz_fitted = np.empty((num_configs, self.__ntv))
        finer_volumes = np.empty((num_configs, self.__ntv))
        for i in range(num_configs):
            strains, finer_volumes[i, :] = interpolate_volumes(self.volumes[i], self.__ntv, 1.05)
            eulerian_strain = calc_eulerian_strain(self.volumes[i][0], self.volumes[i])
            # helmholtz_fitted[i, :] = bmf_energy(eulerian_strain, self.helmoholtz_configs[i], len(self.volumes[i]),
            #                                     strains,
            #                                     finer_volumes,
            #                                     self.__ntv)
            helmholtz_fitted[i, :] = birchmurnaghan_energy(self.helmoholtz_configs[i], eulerian_strain, strains)

        return finer_volumes, helmholtz_fitted

    @LazyProperty
    def finer_volumes(self):
        return self.helmholtz_at_dense_v[0]

    @LazyProperty
    def helmholtz_fitted(self):
        return self.helmholtz_at_dense_v[1]

    @LazyProperty
    def helmholtz_fitted_vref(self):
        f_confv = self.helmholtz_fitted
        volume_confv = self.finer_volumes
        v_desired = self.volumes[0]

        num_configs, ntv = self.helmholtz_fitted.shape
        result = np.empty((num_configs, len(v_desired)))
        f_confv_large = np.hstack((f_confv[:, 3].reshape(-1, 1), f_confv, f_confv[:, -4].reshape(-1, 1)))
        volume_confv_large = np.hstack(
            (volume_confv[:, 3].reshape(-1, 1), volume_confv, volume_confv[:, -4].reshape(-1, 1)))

        v_desired_amount = len(v_desired)
        for i in range(num_configs):
            rs = np.zeros(v_desired_amount)
            vectorized_find_nearest(np.sort(volume_confv_large[i]), v_desired, rs)
            rs = self.__ntv - 1 - rs

            for j in range(v_desired_amount):
                k = int(rs[j])
                x1, x2, x3, x4 = volume_confv_large[i, k - 1:k + 3]
                f1, f2, f3, f4 = f_confv_large[i, k - 1:k + 3]

                result[i, j] = _lagrange4(v_desired[j], x1, x2, x3, x4, f1, f2, f3, f4)
        return result

    @LazyProperty
    def partition_from_helmholtz(self):
        try:
            import bigfloat
        except ImportError:
            raise ImportError(
                "You need to install ``bigfloat`` package to use {0} object!".format(self.__class__.__name__))

        with bigfloat.precision(self.precision):
            return np.array([bigfloat.exp(d) for d in  # shape = (# of volumes for each configuration, 1)
                             logsumexp(-self.helmholtz_fitted_vref.T / (K * self.temperature), axis=1,
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
