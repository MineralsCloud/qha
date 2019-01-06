#!/usr/bin/env python3
"""
.. module statmech
   :platform: Unix, Windows, Mac, Linux
   :synopsis:
.. moduleauthor:: Qi Zhang <qz2280@columbia.edu>
"""

import numpy as np
from numba import float64, vectorize
from scipy.constants import physical_constants as pc

import qha.settings

# ===================== What can be exported? =====================
__all__ = ['ho_free_energy', 'subsystem_partition_function', 'log_subsystem_partition_function']

K = {'ha': pc['Boltzmann constant in eV/K'][0] / pc['Hartree energy in eV'][0],
     'ry': pc['Boltzmann constant in eV/K'][0] / pc['Rydberg constant times hc in eV'][0],
     'ev': pc['Boltzmann constant in eV/K'][0],
     'SI': pc['Boltzmann constant'][0]}[qha.settings.energy_unit]

HBAR = {'ha': 100 / pc['electron volt-inverse meter relationship'][0] / pc['Hartree energy in eV'][0],
        'ry': 100 / pc['electron volt-inverse meter relationship'][0] / pc['Rydberg constant times hc in eV'][0],
        'ev': 100 / pc['electron volt-inverse meter relationship'][0],
        'SI': 100 / pc['electron volt-inverse meter relationship'][0] / pc['joule-electron volt relationship'][0]}[
    qha.settings.energy_unit]


@vectorize([float64(float64, float64)], nopython=True, target='parallel', cache=True)
def ho_free_energy(temperature, frequency):
    """
    Calculate Helmholtz free energy of a single harmonic oscillator at a specific temperature.
    This is a vectorized function so the argument *frequency* can be an array.

    :param temperature: The temperature, in unit 'Kelvin'. Zero-temperature is allowed.
    :param frequency: The frequency of the harmonic oscillator, in unit 'per cm'. If the *frequency*
        is less than or equal to :math:`0`, directly return ``0`` as its free energy.
    :return: Helmholtz free energy of the harmonic oscillator, whose unit depends on user's settings.
    """
    if frequency <= 0:  # Contribution from Gamma point's acoustic frequencies is zero.
        return 0

    hw = HBAR * frequency
    kt = K * temperature
    return 1 / 2 * hw + kt * np.log(1 - np.exp(-hw / kt))


@vectorize([float64(float64, float64)], nopython=True, target='parallel', cache=True)
def subsystem_partition_function(temperature, frequency):
    """
    Calculate the subsystem partition function of a single harmonic oscillator at a specific temperature.
    This is a vectorized function so the argument *frequency* can be an array.

    :param temperature: The temperature, in unit 'Kelvin'. Zero-temperature is allowed.
    :param frequency: The frequency of the harmonic oscillator, in unit 'per cm'. If the *frequency*
        is less than or equal to :math:`0`, directly return ``1`` as its subsystem partition function value.
    :return: The subsystem partition function of the harmonic oscillator.
    """
    if frequency <= 0:
        return 1

    x = -HBAR * frequency / (K * temperature)
    return np.exp(x / 2) / (1 - np.exp(x))


@vectorize([float64(float64, float64)], nopython=True, target='parallel', cache=True)
def log_subsystem_partition_function(temperature, frequency):
    """
    Calculate the natural logarithm of the subsystem partition function of a single harmonic oscillator
    at a specific temperature. This is a vectorized function so the argument *frequency* can be an array.

    :param temperature: The temperature, in unit 'Kelvin'. Zero-temperature is allowed.
    :param frequency: The frequency of the harmonic oscillator, in unit 'per cm'. If the *frequency*
        is less than or equal to :math:`0`, directly return ``0`` as a result.
    :return: Natural logarithm of the subsystem partition function of the oscillator.
    """
    if frequency <= 0:
        return 0

    x = -HBAR * frequency / (K * temperature)
    return x / 2 - np.log(1 - np.exp(x))
