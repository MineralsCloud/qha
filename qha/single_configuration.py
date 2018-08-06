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

    :param temperature: A ``float`` that represents the temperature at which  the total free energy is calculated. This
        value is in unit 'Kelvin'.
    :param q_weights: An :math:`m \\times 1` vector that represents the weight of each q-point in doing Brillouin zone
        sampling. The can be non-normalized, since normalized will be done in the function.
    :param static_energies: An :math:`n \\times 1` vector that represents the static energy of the system with
        :math:`n` different volumes. This should be the same unit as user defined in ``settings.yaml``.
    :param frequencies: An :math:`n \\times m \\times l` 3D array that represents the frequency read from file.
    :param static_only: Just return the static energies, which is got from *static_energies* parameter. This is useful
        when user just wants to see static energies result while keep all other functions the same.
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
    A harmonic oscillator energy sampler. The differences between ``free_energy`` and ``HOFreeEnergySampler`` are

    - ``HOFreeEnergySampler`` provides you with several ways to compute free energies on different q-point, band or
        volume, which could be used to check the correctness of the data.
    - ``HOFreeEnergySampler`` can make calculation lazy, so we can apply it onto a grid, rather than directly
            calculates the values immediately.
    - ``free_energy`` is usually enough for computing the final free energy results. ``HOFreeEnergySampler``
      only calculates its vibrational part, static energies is not counted.

    :param temperature: A ``float`` that represents the temperature at which  the total free energy is calculated. This
        value is in unit 'Kelvin'.
    :param q_weights: An :math:`m \\times 1` vector that represents the weight of each q-point in doing Brillouin zone
        sampling. The can be non-normalized, since normalized will be done in the class.
    :param frequencies: An :math:`n \\times m \\times l` 3D array that represents the frequencies read from file,
        usually may be in unit :math:`\text{cm}^{-1}`.
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
        Used for checking.

        :param i: An integer labeling :math:`i` th q-point.
        :return: The accumulated free energy on the :math:`i` th q-point.
        """
        return ho_free_energy(self.temperature, self.omegas[:, i, :])

    def on_band(self, i: int) -> Matrix:
        """
        Used for checking.

        :param i: An integer labeling :math:`i` th band.
        :return: The accumulated free energy on the :math:`i`th q-point.
        """
        return ho_free_energy(self.temperature, self.omegas[:, :, i])

    def on_volume(self, i: int) -> Scalar:
        """
        Sample free energies on :math:`i` th volume.

        :param i: An integer labeling :math:`i` th volume.
        :return: The accumulated free energy on the :math:`i` th volume.
        """
        return np.vdot(ho_free_energy(self.temperature, self.omegas[i]).sum(axis=1), self._scaled_q_weights)

    @LazyProperty
    def on_all_volumes(self) -> Vector:
        """
        Sample free energies on every volume.

        :return: A vector with length equals to the number of volumes. Each element is the free energy of
            corresponding volume.
        """
        # First calculate free energies on a 3D array, then sum along the third axis (bands),
        # at last contract weights and free energies on all q-points.
        return np.dot(ho_free_energy(self.temperature, self.omegas).sum(axis=2), self._scaled_q_weights)
