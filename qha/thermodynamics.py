#!/usr/bin/env python3
"""
.. module thermodynamics
   :platform: Unix, Windows, Mac, Linux
   :synopsis: Calculate the basic thermodynamic properties for a system: S, U, H, G, Cv on a (T,V) grid.
.. moduleauthor:: Tian Qin <qinxx197@umn.edu>
.. moduleauthor:: Qi Zhang <qz2280@columbia.edu>
"""

import numpy as np

from qha.type_aliases import Matrix, Vector
from qha.v2p import v2p

# ===================== What can be exported? =====================
__all__ = [
    'pressure',
    'entropy',
    'thermodynamic_potentials',
    'volume',
    'thermal_expansion_coefficient',
    'gruneisen_parameter',
    'isothermal_bulk_modulus',
    'adiabatic_bulk_modulus',
    'bulk_modulus_derivative',
    'isobaric_heat_capacity',
    'volumetric_heat_capacity'
]


def calculate_derivatives(xs: Vector, fs: Matrix) -> Matrix:
    """
    Calculate the derivative of :math:`f(x)`, i.e., :math:`\\frac{ df(x) }{ dx }`.

    :param xs: A 1D vector, with length :math:`N_x`.
    :param fs: A matrix, with shape :math:`(N_x, _)`.
    :return: A matrix, with shape :math:`(N_x, _)`.
    """
    if xs.ndim > 1 or fs.ndim < 2:
        raise ValueError('The argument *xs* should be a 1D array and *ys* should be a 2D array!')

    return np.gradient(fs, axis=0) / np.gradient(xs)[:, None]  # df(x)/dx.


def pressure(vs: Vector, free_energies: Matrix) -> Matrix:
    """
    Calculate the pressure as a function of temperature and volume, i.e.,

    .. math::

       P = - \\bigg( \\frac{ \\partial F(T, V) }{ \\partial V } \\bigg)_T.

    :param vs: A vector of volumes.
    :param free_energies: A matrix, the free energy as a function of temperature and volume, i.e., :math:`F(T, V)`.
    :return: A matrix, the pressure as a function of temperature and volume, i.e., :math:`P(T,V)`.
    """
    return -np.gradient(free_energies, axis=1) / np.gradient(vs)


def entropy(temperature: Vector, free_energies: Matrix) -> Matrix:
    """
    Calculate the entropy as a function of temperature and volume, i.e.,

    .. math::

       S = - \\bigg( \\frac{ \\partial F(T, V) }{ \\partial T } \\bigg)_V.

    :param temperature: A vector of temperature.
    :param free_energies: A matrix, the free energy as a function of temperature and volume, i.e., :math:`F(T, V)`.
    :return: A matrix, the entropy as a function of temperature and volume, i.e., :math:`S(T,V)`.
    """
    return -calculate_derivatives(temperature, free_energies)


def thermodynamic_potentials(temperature: Vector, vs: Vector, free_energies: Matrix, ps: Matrix):
    """
    Calculate the enthalpy :math:`H(T, V)`, the internal energy :math:`U(T, V)`,
    and the Gibbs free energy :math:`G` on a :math:`(T, V)` grid from Helmholtz free energy :math:`F(T, V)` by

    .. math::

       U(T, V) &= F(T, V) + T S(T, V), \\\\
       H(T, V) &= U(T, V) + P(T, V) V, \\\\
       G(T, V) &= F(T, V) + P(T, V) V.

    :param temperature: A vector of temperature.
    :param vs: A vector of volumes.
    :param free_energies: A matrix, the free energy as a function of temperature and volume, i.e., :math:`F(T, V)`.
    :param ps: A matrix, the pressure as a function of temperature and volume, i.e., :math:`P(T, V)`.
    :return: A dictionary that contains the enthalpy :math:`H(T, V)`, the internal energy :math:`U(T, V)`,
        and the Gibbs free energy :math:`G` on a :math:`(T, V)` grid. They can be retrieved by ``'U'``, ``'H'``, or
        ``'G'`` keys, respectively.
    """
    g: Matrix = free_energies + ps * vs  # G(T,V) = F(T,V) + V * P(T,V)

    u: Matrix = free_energies + entropy(temperature, free_energies) * temperature.reshape(-1, 1)  # U(T,V) = F(T,V) + T * S(T,V)

    h: Matrix = u + ps * vs  # H(T,V) = U(T,V) + V * P(T,V)

    return {'U': u, 'H': h, 'G': g}


def volume(vs: Vector, desired_ps: Vector, ps: Matrix) -> Matrix:
    """
    Convert the volumes as a function of temperature and pressure, i.e., on a :math:`(T, P)` grid.

    :param vs: A vector of volumes.
    :param desired_ps: A vector of desired pressures.
    :param ps: A matrix, the pressure as a function of temperature and volume, i.e., :math:`P(T,V)`, in atomic unit.
    :return: A matrix, the volume as a function of temperature and pressure, i.e., :math:`V(T, P)`.
    """
    nt, ntv = ps.shape
    vs = vs.reshape(1, -1).repeat(nt, axis=0)
    return v2p(vs, ps, desired_ps)


def thermal_expansion_coefficient(temperature: Vector, vs: Matrix) -> Matrix:
    """
    Calculate the thermal expansion coefficient by

    .. math::

       \\alpha = \\frac{ 1 }{ V }  \\bigg( \\frac{ \\partial V }{ \\partial T } \\bigg)_P.

    :param temperature: A vector of temperature.
    :param vs: A matrix, the volume as a function of temperature and pressure, i.e., :math:`V(T, P)`.
    :return: A matrix, the thermal expansion coefficient as a function of temperature and pressure,
        i.e., :math:`\\alpha(T, P)`.
    """
    # Division is done by element-wise.
    return calculate_derivatives(temperature, vs) / vs


def gruneisen_parameter(vs: Matrix, bt: Matrix, alpha: Matrix, cv: Matrix) -> Matrix:
    """
    Calculate the Grüneisen parameter by

    .. math::

       \\gamma = \\frac{ \\alpha B_T V }{ C_V }.

    :param vs: A matrix, the volume as a function of temperature and pressure, i.e., :math:`V(T, P)`.
    :param bt: A matrix, the isothermal bulk modulus as a function of temperature and pressure,
        i.e., :math:`B_T(T, P)`.
    :param alpha: A matrix, the thermal expansion coefficient as a function of temperature and pressure,
        i.e., :math:`\\alpha(T, P)`.
    :param cv: A matrix, the volumetric heat capacity as a function of temperature and pressure,
        i.e., :math:`C_V(T, P)`.
    :return: A matrix, the thermodynamic Grüneisen parameter as a function of temperature and pressure,
        i.e., :math:`\\gamma(T, P)`.
    """
    gamma = np.empty([vs.shape[0], vs.shape[1]])
    gamma[0] = 0.0
    gamma[1:, :] = vs[1:] * bt[1:] * alpha[1:] / cv[1:]
    # return vs * bt * alpha / cv
    return gamma


def isothermal_bulk_modulus(vs: Vector, ps: Matrix) -> Matrix:
    """
    Calculate the isothermal bulk modulus by

    .. math::

       B_T = - V \\bigg( \\frac{ \\partial P }{ \\partial V } \\bigg)_T.

    :param vs: A vector of volumes.
    :param ps: A matrix, the pressure as a function of temperature and volume, i.e., :math:`P(T, V)`.
    :return: A matrix, the isothermal bulk modulus, as a function of temperature and volume, i.e., :math:`B_T(T, V)`.
    """
    return -np.gradient(ps, axis=1) / np.gradient(vs) * vs


def adiabatic_bulk_modulus(bt: Matrix, alpha: Matrix, gamma: Matrix, temperature: Vector) -> Matrix:
    """
    Calculate the adiabatic bulk modulus by

    .. math::

       B_S = B_T \\big( 1 + \\alpha \\gamma T \\big).

    :param bt: A matrix, the isothermal bulk modulus, as a function of temperature and pressure,
        i.e., :math:`B_T(T, P)`.
    :param alpha: A matrix, the thermal expansion coefficient as a function of temperature and pressure,
        i.e., :math:`\\alpha(T, P)`.
    :param gamma: A matrix, the thermodynamic Grüneisen parameter as a function of temperature and pressure,
        i.e., :math:`\\gamma(T, P)`.
    :param temperature: A vector of temperature.
    :return: A matrix, the adiabatic bulk modulus, as a function of temperature and pressure,
        i.e., :math:`B_S(T,P)`.
    """
    return bt * (1.0 + alpha * gamma * temperature[:, None])


def bulk_modulus_derivative(ps: Vector, bt: Matrix) -> Matrix:
    """
    Calculate the first-order derivative of bulk modulus with respect to pressure by

    .. math::

       B_T' = \\bigg( \\frac{ \\partial B_T }{ \\partial P } \\bigg).

    :param ps: A vector of pressures.
    :param bt: A matrix, the isothermal bulk modulus, as a function of temperature and pressure,
        i.e., :math:`B_T(T, P)`.
    :return: A matrix, the isothermal bulk modulus, as a function of temperature and pressure, i.e.,
        :math:`B_T'(T, P)`.
    """
    return calculate_derivatives(ps, bt.T).T


def isobaric_heat_capacity(cv: Matrix, alpha: Matrix, gamma: Matrix, temperature: Vector) -> Matrix:
    """
    Calculate the isobaric heat capacity by

    .. math::

       C_P = C_V \\big( 1 + \\alpha \\gamma T \\big).

    :param cv: A matrix, the volumetric heat capacity, :math:`C_V(T, P)`.
    :param alpha: A matrix, the thermal expansion coefficient as a function of temperature and pressure,
        i.e., :math:`\\alpha(T, P)`.
    :param gamma: A matrix, the thermodynamic Grüneisen parameter as a function of temperature and pressure,
        i.e., :math:`\\gamma(T, P)`.
    :param temperature: A vector of temperature.
    :return: A matrix, the isobaric specific heat capacity as a function of temperature and pressure,
        i.e., :math:`C_P(T,P)`.
    """
    return cv * (1.0 + alpha * gamma * temperature[:, None])


def volumetric_heat_capacity(temperature: Vector, internal_energies: Matrix) -> Matrix:
    """
    Calculate the volumetric heat capacity by

    .. math::

       C_V = \\bigg( \\frac{ \\partial U }{ \\partial T } \\bigg).

    :param temperature: A vector of temperature.
    :param internal_energies: A matrix, the internal energy as a function of temperature and volume,
        i.e., :math:`U(T, V)`.
    :return: A matrix, the volumetric heat capacity as a function of temperature and volume,
        i.e., :math:`C_V(T, V)`.
    """
    return calculate_derivatives(temperature, internal_energies)
