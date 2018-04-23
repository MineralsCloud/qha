#!/usr/bin/env python3
"""
:mod:`statmech` -- Statistical mechanics
========================================

.. module statmech
   :platform: Unix, Windows, Mac, Linux
   :synopsis:
.. moduleauthor:: Qi Zhang <qz2280@columbia.edu>
"""

import numpy as np
from numba import float64, vectorize
from scipy.constants import Boltzmann

import qha.settings

# ===================== What can be exported? =====================
__all__ = ['ho_free_energy', 'subsystem_partition_function', 'log_subsystem_partition_function']

K = {'ha': 8.617e-5 / 13.6058 / 2,
     'ry': 8.617e-5 / 13.6058,
     'ev': 8.617e-5,
     'SI': Boltzmann}[qha.settings.energy_unit]

HBAR = {'ha': 1.23984193e-4 / 13.6058 / 2,
        'ry': 1.23984193e-4 / 13.6058,
        'ev': 1.23984193e-4,
        'SI': 1.986e-23}[qha.settings.energy_unit]


@vectorize([float64(float64, float64)], nopython=True, target='parallel', cache=True)
def ho_free_energy(temperature, frequency):
    """
    Helmholtz free energy for a single harmonic oscillator.

    :param frequency: The frequency of the harmonic oscillator, in unit 'per cm'. If *omega* is less than or equal to
        `0`, just return `0` as its free energy.
    :param temperature: The temperature, in unit 'Kelvin'. Zero-temperature is also OK.
    :return: Helmholtz free energy for the harmonic oscillator, in unit 'electron volt'.
    """
    if frequency <= 0:  # Contribution from Gamma point's acoustic frequencies is zero.
        return 0

    hw = HBAR * frequency
    kt = K * temperature
    return 1 / 2 * hw + kt * np.log(1 - np.exp(-hw / kt))


@vectorize([float64(float64, float64)], nopython=True, target='parallel', cache=True)
def subsystem_partition_function(temperature, frequency):
    """
    Partition function for one oscillator.

    :param frequency: The frequency of the harmonic oscillator, in unit 'per cm'. If *omega* is less than or equal to
        `0`, just return `1` as its subsystem_partition_function.
    :param temperature: The temperature, in unit 'Kelvin'. Zero-temperature is also OK.
    :return: Partition function for the oscillator.
    """
    if frequency <= 0:
        return 1

    x = -HBAR * frequency / (K * temperature)
    return np.exp(x / 2) / (1 - np.exp(x))


@vectorize([float64(float64, float64)], nopython=True, target='parallel', cache=True)
def log_subsystem_partition_function(temperature, frequency):
    """
    A natural logarithm of ``subsystem_partition_function``.

    :param temperature: The temperature, in unit 'Kelvin'. Zero-temperature is also OK.
    :param frequency: The frequency of the harmonic oscillator, in unit 'per cm'. If *omega* is less than or equal to
        `0`, just return `1` as its subsystem_partition_function.
    :return: Natural logarithm of partition function for the oscillator.
    """
    if frequency <= 0:
        return 0

    x = -HBAR * frequency / (K * temperature)
    return x / 2 - np.log(1 - np.exp(x))
