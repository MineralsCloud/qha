#!/usr/bin/env python3
"""
.. module multi_configurations.different_phonon_dos
   :platform: Unix, Windows, Mac, Linux
.. moduleauthor:: Qi Zhang <qz2280@columbia.edu>
.. moduleauthor:: Tian Qin <qinxx197@umn.edu>
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
    """
    A class that represents the partition function of multiple configurations with different phonon density of states.
    In mathematics, it is represented as

    .. math::

       Z_{\\text{all configs}}(T, V) = \\sum_{j = 1}^{N_{c}} g_{j} Z_{j}(T, V),

    where :math:`N_{c}` stands for the number of configurations and :math:`g_{j}` stands for degeneracy for the
    :math:`j` th configuration.

    :param temperature: The temperature at which the partition function is calculated.
    :param degeneracies: An array of degeneracies of each configuration, which will not be normalized in the
        calculation. They should all be positive integers.
    :param q_weights: The weights of all q-points that are sampled, can be a 2D matrix so each configuration can have
        a little bit different q-point weights, but the number of q-points of each configuration must be the same.
    :param static_energies: The static energy of each configuration of each volume.
    :param volumes: A matrix of volumes of each configuration, should have the same values for each
        configuration.
    :param frequencies: A 4D array that specifies the frequency on each configuration, volume, q-point and mode.
    :param static_only: Whether the calculation only takes static contribution and does not consider
        the vibrational contribution, by default, is ``False``.
    :param precision: The precision of a big float number to represent the partition function since it is a very large
        value, by default, is ``500``.
    :param order: The order of Birch--Murnaghan equation of state fitting, by default, is ``3``.
    """

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
    def unaligned_free_energies_for_each_configuration(self):
        """
        If the input free energy is not aligned for each configuration, first just calculate the "raw"
        free energy on each volume and each configuration.

        :return: A matrix, the "raw" free energy of each configuration of each volume.
        """
        configurations_amount, _ = self.volumes.shape
        return np.array([free_energy(self.temperature, self.q_weights[i], self.static_energies[i], self.frequencies[i],
                                     self.static_only) for i in range(configurations_amount)])

    @LazyProperty
    def aligned_free_energies_for_each_configuration(self):
        """
        Then do a fitting to align all these free energies.

        :return: A matrix, the aligned free energy of each configuration of each volume.
        """
        return calibrate_energy_on_reference(self.volumes, self.unaligned_free_energies_for_each_configuration,
                                             self.order)

    @LazyProperty
    def partition_functions_for_each_configuration(self):
        """
        Inversely solve the free energy to get partition function for :math:`j` th configuration by

        .. math::

           Z_{j}(T, V) = \\exp \\bigg( -\\frac{ F_{j}(T, V) }{ k_B T } \\bigg).

        :return: A matrix, the partition function of each configuration of each volume.
        """
        try:
            import mpmath
        except ImportError:
            raise ImportError("Install ``mpmath`` package to use {0} object!".format(self.__class__.__name__))

        with mpmath.workprec(self.precision):
            # shape = (# of configurations, # of volumes for each configuration)
            exp = np.vectorize(bigfloat.exp)
            return exp(-self.aligned_free_energies_for_each_configuration / (K * self.temperature))

    @LazyProperty
    def partition_functions_for_all_configurations(self):
        """
        Sum the partition functions for all configurations.

        .. math::

           Z_{\\text{all configs}}(T, V) = \\sum_{j} Z_{j}(T, V).

        :return: A vector, the partition function of each volume.
        """
        try:
            import mpmath
        except ImportError:
            raise ImportError("Install ``mpmath`` package to use {0} object!".format(self.__class__.__name__))

        with mpmath.workprec(self.precision):
            # shape = (# of volumes,)
            return np.array([mpmath.exp(d) for d in
                             logsumexp(-self.aligned_free_energies_for_each_configuration.T / (K * self.temperature),
                                       axis=1, b=self.degeneracies)])

    def get_free_energies(self):
        """
        The free energy calculated from the partition function :math:`Z_{\\text{all configs}}(T, V)` by

        .. math::

           F_{\\text{all configs}}(T, V) = - k_B T \\ln Z_{\\text{all configs}}(T, V).

        :return: The free energy on a temperature-volume grid.
        """
        try:
            import mpmath
        except ImportError:
            raise ImportError("Install ``mpmath`` package to use {0} object!".format(self.__class__.__name__))

        with mpmath.workprec(self.precision):
            log_z = np.array([mpmath.log(d) for d in self.partition_functions_for_all_configurations], dtype=float)
        return -K * self.temperature * log_z
