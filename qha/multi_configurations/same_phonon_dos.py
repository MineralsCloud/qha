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
    """
    A class that represents the partition function of multiple configurations with same phonon density of states.
    In mathematics, it is represented as

    .. math::

        Z_{\\text{all configs}}(T, V) = \sum_{j = 1}^{N_{c}}
        \\bigg\{
        g_{j} \exp \\Big( -\\frac{ E_j(V) }{ k_B T } \\Big)
        \prod_{\mathbf{q}s} \\bigg(
        \\frac{\exp \\Big( -\\frac{ \hbar \omega_{\mathbf{ q }s}(V) }{ 2 k_B T } \Big)}{1 - \exp \\Big( -\\frac{ \hbar \omega_{\mathbf{ q }s}(V) }{ k_B T } \\Big)}
        \\bigg)
        \\bigg\}.

    :param temperature: The temperature at which partition function is calculated.
    :param degeneracies: An array of degeneracies of each configurations, which will not be normalized in calculation.
        Should be all positive integers.
    :param q_weights: The weights of all q-points that are sampled, can be an array so each configuration should
        have the same q-weights.
    :param static_energies: The static energy of each configuration of each volume.
    :param frequencies: A 3D array that specifies the frequency on the specified configuration, volume, q-point
        and mode.
    :param precision: The precision of a big float number to represent the partition function since it is a very large
        number, by default is ``500``.
    """

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

    @property
    def _static_part(self) -> Vector:
        """
        Static contribution to the partition function.

        :return: Static contribution on the temperature-volume mesh.
        """
        try:
            import bigfloat
        except ImportError:
            raise ImportError(
                "You need to install ``bigfloat`` package to use {0} object!".format(self.__class__.__name__))

        with bigfloat.precision(self.precision):
            return np.array([bigfloat.exp(d) for d in  # shape = (# of volumes for each configuration, 1)
                             logsumexp(-self.static_energies / (K * self.temperature), axis=1, b=self.degeneracies)])

    @property
    def _harmonic_part(self) -> Vector:
        """
        Harmonic contribution to the partition function.

        :return: Harmonic contribution on the temperature-volume mesh.
        """
        log_product_modes: Matrix = np.sum(
            log_subsystem_partition_function(self.temperature, self.frequencies), axis=2, dtype=float)
        return np.exp(np.dot(log_product_modes, self._scaled_q_weights))  # (vol, 1)

    @LazyProperty
    def total(self) -> Vector:
        """
        Total partition function.

        :return: Partition function on the temperature-volume mesh.
        """
        return np.multiply(self._static_part, self._harmonic_part)  # (vol, 1), product element-wise

    def get_free_energies(self):
        """
        Give free energy by

        .. math::

             F_{\\text{all configs}}(T, V) = - k_B T \ln Z_{\\text{all configs}}(T, V).

        :return: Free energy on the temperature-volume mesh.
        """
        try:
            import bigfloat
        except ImportError:
            raise ImportError(
                "You need to install ``bigfloat`` package to use {0} object!".format(self.__class__.__name__))

        with bigfloat.precision(self.precision):
            log_z = np.array([bigfloat.log(d) for d in self.total], dtype=float)
        return -K * self.temperature * log_z


class FreeEnergy:
    """
    A class that represents the free energy of multiple configurations with same phonon density of states.
    In mathematics, it is represented as

    .. math::

        F_{\\text{all configs}}(T, V) = - k_B T \ln Z_{\\text{all configs}}(T, V)
        = - k_B T \ln \\bigg( \sum_{j = 1}^{N_{c}} g_{j} \exp \\Big( -\\frac{ E_j(V) }{ k_B T } \\Big) \\bigg)
        + \sum_{\mathbf{ q }s} \\bigg\{ \\frac{ \hbar \omega_{\mathbf{ q }s}(V) }{ 2 }
            + k_B \ln \\bigg( 1 - \exp \\Big( -\\frac{ \hbar \omega_{\mathbf{ q }s}(V) }{ k_B T } \\Big) \\bigg)
        \\bigg\}.

    :param temperature: The temperature at which partition function is calculated.
    :param degeneracies: An array of degeneracies of each configurations, which will not be normalized in calculation.
        Should be all positive integers.
    :param q_weights: The weights of all q-points that are sampled, can be an array so each configuration should
        have the same q-weights.
    :param static_energies: The static energy of each configuration of each volume.
    :param volumes: A matrix of array of volumes of each configurations, should have the same number for each
        configuration.
    :param frequencies: A 3D array that specifies the frequency on the specified configuration, volume, q-point
        and mode.
    :param static_only: If the calculation only takes static energy and does not consider vibrational contribution,
        by default is ``False``.
    :param order: The order of Birch--Murnaghan equation of state fitting, by default is ``3``.
    """

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
    def aligned_static_energies_for_each_configuration(self):
        """
        If your input static energy is not aligned for each configuration, then do a
        fitting to align all these static energy.

        :return: A matrix of aligned static energy of each configuration of each volume.
        """
        return calibrate_energy_on_reference(self.volumes, self.static_energies, self.order)

    @LazyProperty
    def static_part(self) -> Vector:
        """
        Static contribution to the free energy.

        :return: Static contribution on the temperature-volume mesh.
        """
        kt: float = K * self.temperature  # k_B T
        inside_exp: Matrix = -self.aligned_static_energies_for_each_configuration.T / kt  # exp( E_n(V) / k_B / T )
        return -kt * logsumexp(inside_exp, axis=1, b=self.degeneracies)

    @LazyProperty
    def harmonic_part(self) -> Vector:
        """
        Harmonic contribution to the free energy.

        :return: Harmonic contribution on the temperature-volume mesh.
        """
        sum_modes = np.sum(ho_free_energy(self.temperature, self.frequencies), axis=2)
        return np.dot(sum_modes, self._scaled_q_weights)

    @LazyProperty
    def total(self) -> Vector:
        """
        Total partition function. Static part plus harmonic part.

        :return: Total free energy on the temperature-volume mesh.
        """
        return self.static_part + self.harmonic_part

    def get_free_energies(self):
        """
        If you specify ``static_only = True`` in class initialization, then here only static contribution will
        be returned, this is equivalent to the ``static_part`` property. If not, then this is equivalent to
        the ``total`` property.

        :return: Free energy on the temperature-volume mesh.
        """
        if self.static_only:
            return self.static_part

        return self.total
