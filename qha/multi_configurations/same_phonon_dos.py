#!/usr/bin/env python3
"""
.. module multi_configurations.same_phonon_dos
   :platform: Unix, Windows, Mac, Linux
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
    A class that represents the partition function of multiple configurations with the same phonon density of states.
    In mathematics, it is represented as

    .. math::

       Z_{\\text{all configs}}(T, V) = \\sum_{j = 1}^{N_{c}} g_{j}
       \\bigg\\{
         \\exp \\Big( -\\frac{ E_j(V) }{ k_B T } \\Big)
         \\prod_{\\mathbf{q}s} \\bigg(
           \\tfrac{\\exp \\big(-\\tfrac{ \\hbar \\omega_{\\mathbf{ q }s}^j(V) }{ 2 k_B T }\\big)}{1 - \\exp \\big(-\\tfrac{ \\hbar \\omega_{\\mathbf{ q }s}^j(V) }{ k_B T }\\big)}
         \\bigg)^{w_{\\mathbf{ q }}^j}
       \\bigg\\}.

    :param temperature: The temperature at which the partition function is calculated.
    :param degeneracies: An array of degeneracies of each configuration, which will not be normalized in the
        calculation. They should all be positive integers.
    :param q_weights: The weights of all q-points that are sampled, should be a vector since all configurations should
        have the same q-point weights.
    :param static_energies: The static energies of each configuration of each volume.
    :param frequencies: It is a 3D array that specifies the frequency on each volume, q-point and mode.
        It is not 4D since we have all configurations sharing the same phonon density of states.
    :param precision: The precision of a big float number to represent the partition function since it is a very large
        value, by default, is ``500``.
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
        Calculate the static contribution to the partition function.

        :return: The static contribution on the temperature-volume grid.
        """
        try:
            import mpmath
        except ImportError:
            raise ImportError(
                "You need to install ``mpmath`` package to use {0} object!".format(self.__class__.__name__))

        with mpmath.workprec(self.precision):
            return np.array([mpmath.exp(d) for d in  # shape = (# of volumes for each configuration, 1)
                             logsumexp(-self.static_energies / (K * self.temperature), axis=1, b=self.degeneracies)])

    @property
    def _harmonic_part(self) -> Vector:
        """
        Calculate the harmonic contribution to the partition function.

        :return: The harmonic contribution on the temperature-volume grid.
        """
        log_product_modes: Matrix = np.sum(
            log_subsystem_partition_function(self.temperature, self.frequencies), axis=2, dtype=float)
        return np.exp(np.dot(log_product_modes, self._scaled_q_weights))  # (vol, 1)

    @LazyProperty
    def total(self) -> Vector:
        """
        Calculate the total partition function.

        :return: The partition function on the temperature-volume grid.
        """
        return np.multiply(self._static_part, self._harmonic_part)  # (vol, 1), product element-wise

    def get_free_energies(self):
        """
        Give the free energy by

        .. math::

           F_{\\text{all configs}}(T, V) = - k_B T \\ln Z_{\\text{all configs}}(T, V).

        :return: The free energy on the temperature-volume grid.
        """
        try:
            import mpmath
        except ImportError:
            raise ImportError("Install ``mpmath`` package to use {0} object!".format(self.__class__.__name__))

        with mpmath.workprec(self.precision):
            log_z = np.array([mpmath.log(d) for d in self.total], dtype=float)
        return -K * self.temperature * log_z


class FreeEnergy:
    """
    A class that represents the free energy of multiple configurations with the same phonon density of states.
    In mathematics, it is represented as

    .. math::

       F_{\\text{all configs}}(T, V) = - k_B T \\ln Z_{\\text{all configs}}(T, V)
       = - k_B T \\ln \\bigg( \\sum_{j = 1}^{N_{c}} g_{j} \\exp \\Big( -\\frac{ E_j(V) }{ k_B T } \\Big) \\bigg)
         + \\sum_{\\mathbf{ q }s} w_\\mathbf{ q }
             \\bigg\\{ \\frac{ \\hbar \\omega_{\\mathbf{ q }s}(V) }{ 2 }
             + k_B \\ln \\bigg( 1 - \\exp \\Big( -\\frac{ \\hbar \\omega_{\\mathbf{ q }s}(V) }{ k_B T } \\Big) \\bigg)
         \\bigg\\}.

    :param temperature: The temperature at which the partition function is calculated.
    :param degeneracies: An array of degeneracies of each configuration, which will not be normalized in the
        calculation. They should all be positive integers.
    :param q_weights: The weights of all q-points that are sampled, should be a vector since all configurations should
        have the same q-point weights.
    :param static_energies: The static energy of each configuration of each volume.
    :param volumes: A matrix of volumes of each configurations, should have the same values for each
        configuration.
    :param frequencies: It is a 3D array that specifies the frequency on each volume, q-point and mode.
        It is not 4D since we have all configurations sharing the same phonon density of states.
    :param static_only: Whether the calculation only takes static contribution and does not consider
        the vibrational contribution, by default, is ``False``.
    :param order: The order of Birch--Murnaghan equation of state fitting, by default, is ``3``.
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
        If the input static energies are not aligned for each configuration, then do a
        fitting to align all static energies.

        :return: A matrix of aligned static energy of each configuration of each volume.
        """
        return calibrate_energy_on_reference(self.volumes, self.static_energies, self.order)

    @LazyProperty
    def static_part(self) -> Vector:
        """
        Calculate the static contribution to the free energy.

        :return: The static contribution on the temperature-volume grid.
        """
        kt: float = K * self.temperature  # k_B T
        inside_exp: Matrix = -self.aligned_static_energies_for_each_configuration.T / kt  # exp( E_n(V) / k_B / T )
        return -kt * logsumexp(inside_exp, axis=1, b=self.degeneracies)

    @LazyProperty
    def harmonic_part(self) -> Vector:
        """
        Calculate the harmonic contribution to the free energy.

        :return: The harmonic contribution on the temperature-volume grid.
        """
        sum_modes = np.sum(ho_free_energy(self.temperature, self.frequencies), axis=2)
        return np.dot(sum_modes, self._scaled_q_weights)

    @LazyProperty
    def total(self) -> Vector:
        """
        Calculate the total partition function, which is the static part plus the harmonic part.

        :return: Total free energy on the temperature-volume grid.
        """
        return self.static_part + self.harmonic_part

    def get_free_energies(self):
        """
        If ``static_only = True`` is specified in class instantiation, then only the static contribution will
        be counted. Then it is equivalent to the ``static_part`` property. If not, then this is equivalent to
        the ``total`` property.

        :return: The free energy on the temperature-volume grid.
        """
        if self.static_only:
            return self.static_part

        return self.total
