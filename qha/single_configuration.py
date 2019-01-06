#!/usr/bin/env python3
"""
.. module single_configuration
   :platform: Unix, Windows, Mac, Linux
   :synopsis: Free energy calculator for a single configuration.
.. moduleauthor:: Qi Zhang <qz2280@columbia.edu>
"""

import numpy as np
from lazy_property import LazyProperty
from numba import jit, float64, boolean

from qha.statmech import ho_free_energy
from qha.type_aliases import Scalar, Vector, Matrix, Array3D

# ===================== What can be exported? =====================
__all__ = ['free_energy', 'HOFreeEnergySampler']


@jit(float64[:](float64, float64[:], float64[:], float64[:, :, :], boolean), cache=True)
def free_energy(temperature: Scalar, q_weights: Vector, static_energies: Vector, frequencies: Array3D,
                static_only: bool = False) -> Vector:
    """
    The total free energy at a certain temperature.

    :param temperature: A ``float`` that represents the temperature at which the total free energy is calculated. This
        value is in unit 'Kelvin'.
    :param q_weights: An :math:`m \\times 1` vector that represents the weight of each q-point in Brillouin zone
        sampling. This vector can be non-normalized since a normalization will be done internally.
    :param static_energies: An :math:`n \\times 1` vector that represents the static energy of the system with
        :math:`n` different volumes. This should be the same unit as user-defined in the "settings" file.
    :param frequencies: An :math:`n \\times m \\times l` 3D array that represents the frequency read from file.
    :param static_only: If ``True``, directly return the static energies, i.e., the *static_energies* parameter itself.
        This is useful when the user just wants to see static result while keeping all other functions unchanged.
    :return: An :math:`n \\times 1` vector that represents the total free energy of the system with :math:`n` different
        volumes. The default unit is the same as in function ``ho_free_energy``.
    """
    if not np.all(np.greater_equal(q_weights, 0)):
        raise ValueError('Weights should all be greater equal than 0!')

    if static_only:
        return static_energies

    scaled_q_weights: Vector = q_weights / np.sum(q_weights)
    vibrational_energies: Vector = np.dot(ho_free_energy(temperature, frequencies).sum(axis=2), scaled_q_weights)
    return static_energies + vibrational_energies


class HOFreeEnergySampler:
    """
    A harmonic oscillator free energy sampler. The differences between ``free_energy`` and ``HOFreeEnergySampler`` are

    - ``HOFreeEnergySampler`` provides several ways to compute free energies on different q-points, bands or
        volumes, which could be used to check the correctness of the data.
    - ``HOFreeEnergySampler`` can make calculation lazy, rather than directly calculates the values immediately.
    - ``free_energy`` is usually enough for computing the final free energy results. ``HOFreeEnergySampler``
      only calculates its vibrational part, static energies are not taken into account.

    :param temperature: A ``float`` that represents the temperature at which the total free energy is calculated. This
        value is in unit 'Kelvin'.
    :param q_weights: An :math:`m \\times 1` vector that represents the weight of each q-point in Brillouin zone
        sampling. This vector can be non-normalized since a normalization will be done internally.
    :param frequencies: An :math:`n \\times m \\times l` 3D array that represents the frequencies read from a file,
        usually in unit :math:`\\text{cm}^{-1}`.
    """

    def __init__(self, temperature: float, q_weights: Vector, frequencies: Array3D):
        self.temperature = temperature  # Fix temperature and volume, just sample q-points and bands
        self.q_weights = np.array(q_weights, dtype=float)
        self.omegas = np.array(frequencies, dtype=float)
        if not np.all(np.greater_equal(q_weights, 0)):
            raise ValueError('Weights should all be greater equal than 0!')
        else:
            self._scaled_q_weights = q_weights / np.sum(q_weights)

    def on_q_point(self, i: int) -> Matrix:  # E1(i,m)
        """
        Sample free energy on the :math:`i` th q-point.

        :param i: An integer labeling :math:`i` th q-point.
        :return: The accumulated free energy on the :math:`i` th q-point.
        """
        return ho_free_energy(self.temperature, self.omegas[:, i, :])

    def on_band(self, i: int) -> Matrix:
        """
        Sample free energy on the :math:`i` th band.

        :param i: An integer labeling :math:`i` th band.
        :return: The accumulated free energy on the :math:`i`th q-point.
        """
        return ho_free_energy(self.temperature, self.omegas[:, :, i])

    def on_volume(self, i: int) -> Scalar:
        """
        Sample free energy on the :math:`i` th volume.

        :param i: An integer labeling :math:`i` th volume.
        :return: The accumulated free energy on the :math:`i` th volume.
        """
        return np.vdot(ho_free_energy(self.temperature, self.omegas[i]).sum(axis=1), self._scaled_q_weights)

    @LazyProperty
    def on_all_volumes(self) -> Vector:
        """
        Sample free energies on every volume.

        :return: A vector with length equals the number of volumes. Each element is the free energy of
            one volume.
        """
        # First calculate free energies on a 3D array, then sum along the third axis (bands),
        # at last contract weights and free energies on all q-points.
        return np.dot(ho_free_energy(self.temperature, self.omegas).sum(axis=2), self._scaled_q_weights)
