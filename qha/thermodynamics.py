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
    'pressures',
    'entropy',
    'thermodynamic_potentials',
    'volumes',
    'thermal_expansion_coefficient',
    'gruneisen_parameter',
    'isothermal_bulk_modulus',
    'adiabatic_bulk_modulus',
    'bulk_modulus_derivative',
    'pressure_specific_heat_capacity',
    'volume_specific_heat_capacity'
]


def calculate_derivatives(xs: Vector, fs: Matrix) -> Matrix:
    """
    Calculate the derivative of :math:`f(x)`, i.e., :math:`\\frac{ df(x) }{ dx }`.

    :param xs: A 1D vector, with length :math:`N_x`.
    :param fs: A 2D matrix, with shape :math:`(N_x, _)`.
    :return: A 2D matrix, with shape :math:`(N_x, _)`.
    """
    if xs.ndim > 1 or fs.ndim < 2:
        raise ValueError('The argument *xs* should be a 1D array and *ys* should be a 2D array!')

    return np.gradient(fs, axis=0) / np.gradient(xs)[:, None]  # df(x)/dx.


def pressures(vs: Vector, free_energies: Matrix) -> Matrix:
    """
    Calculate the pressure as a function of temperature and volume, i.e.,

    .. math::

       P = - \\bigg( \\frac{ \\partial F(T, V) }{ \\partial V } \\bigg)_T.

    :param vs: A vector of volumes.
    :param free_energies: A 2D matrix, the free energy as a function of temperature and volume, i.e., :math:`F(T, V)`.
    :return: A 2D matrix, the pressure as a function of temperature and volume, i.e., :math:`P(T,V)`.
    """
    return -np.gradient(free_energies, axis=1) / np.gradient(vs)


def entropy(ts: Vector, free_energies: Matrix) -> Matrix:
    """
    Calculate the entropy as a function of temperature and volume, i.e.,

    .. math::

       S = - \\bigg( \\frac{ \\partial F(T, V) }{ \\partial T } \\bigg)_V.

    :param ts: A vector of temperature.
    :param free_energies: A 2D matrix, the free energy as a function of temperature and volume, i.e., :math:`F(T, V)`.
    :return: A 2D matrix, the entropy as a function of temperature and volume, i.e., :math:`S(T,V)`.
    """
    return -calculate_derivatives(ts, free_energies)


def thermodynamic_potentials(ts: Vector, vs: Vector, free_energies: Matrix, ps: Matrix):
    """
    Calculate the enthalpy :math:`H(T, V)`, the internal energy :math:`U(T, V)`,
    and the Gibbs free energy :math:`G` on a :math:`(T, V)` grid from Helmholtz free energy :math:`F(T, V)` by

    .. math::

       U(T, V) &= F(T, V) + T S(T, V), \\\\
       H(T, V) &= U(T, V) + P(T, V) V, \\\\
       G(T, V) &= F(T, V) + P(T, V) V.

    :param free_energies: A 2D matrix, the free energy as a function of temperature and volume, i.e., :math:`F(T, V)`.
    :param ps: A 2D matrix, the pressure as a function of temperature and volume, i.e., :math:`P(T,V)`.
    :param ts: A vector of temperature.
    :param vs: A vector of volumes.
    :return: A dictionary that contains the enthalpy :math:`H(T, V)`, the internal energy :math:`U(T, V)`,
        and the Gibbs free energy :math:`G` on a :math:`(T, V)` grid. They can be retrieved by ``'U'``, ``'H'``, or
        ``'G'`` keys, respectively.
    """
    g: Matrix = free_energies + ps * vs  # G(T,V) = F(T,V) + V * P(T,V)

    u: Matrix = free_energies + entropy(ts, free_energies) * ts.reshape(-1, 1)  # U(T,V) = F(T,V) + T * S(T,V)

    h: Matrix = u + ps * vs  # H(T,V) = U(T,V) + V * P(T,V)

    return {'U': u, 'H': h, 'G': g}


def volumes(vs: Vector, desired_ps: Vector, ps: Matrix) -> Matrix:
    """
    Convert the volumes as a function of temperature and pressure, i.e., on a :math:`(T, P)` grid.

    :param vs: A vector of volumes.
    :param desired_ps: A vector of desired pressures.
    :param ps: A 2D matrix, the pressure as a function of temperature and volume, i.e., :math:`P(T,V)`, in atomic unit.
    :return: A 2D matrix, the volume as a function of temperature and pressure, i.e., :math:`V(T, P)`.
    """
    nt, ntv = ps.shape
    v_tv = vs.reshape(1, -1).repeat(nt, axis=0)
    v_tp = v2p(v_tv, ps, desired_ps)
    return v_tp


def thermal_expansion_coefficient(ts: Vector, vs: Matrix) -> Matrix:
    """
    Calculate the thermal expansion coefficient by

    .. math::

       \\alpha = \\frac{ 1 }{ V }  \\left ( \\frac{ \\partial V }{ \\partial T } \\right ).

    :param ts: A vector of temperature.
    :param vs: A 2D matrix, the volume as a function of temperature and pressure, i.e., :math:`V(T, P)`.
    :return: A 2D matrix, the thermal expansion coefficient as a function of temperature and pressure,
        i.e., :math:`\\alpha(T, P)`.
    """
    # Division is done by element-wise.
    return calculate_derivatives(ts, vs) / vs


def gruneisen_parameter(vs: Matrix, bt: Matrix, alpha_tp: Matrix, cv_tp: Matrix) -> Matrix:
    """
    Calculate the Grüneisen parameter by

    .. math::

       \\gamma = \\alpha B_{t} V / Cv.

    :param vs: A 2D matrix, the volume as a function of temperature and pressure, i.e., :math:`V(T, P)`.
    :param bt: A 2D matrix, the isothermal bulk modulus as a function of temperature and pressure,
        i.e., :math:`B_T(T, P)`.
    :param alpha_tp: A 2D matrix, the thermal expansion coefficient as a function of temperature and pressure,
        i.e., :math:`\\alpha(T, P)`.
    :param cv_tp: the volumetric specific heat capacity, :math:`Cv(T,P)`
    :return: thermodynamic gruneisen parameter, :math:`\\gamma(T,P)`
    """
    gamma = np.empty([vs.shape[0], vs.shape[1]])
    gamma[0] = 0.0
    gamma[1:, :] = vs[1:] * bt[1:] * alpha_tp[1:] / cv_tp[1:]
    # return vs * bt_tp_au * alpha_tp / cv_tp_au
    return gamma


def isothermal_bulk_modulus(v_vector: Vector, p_tv: Matrix) -> Matrix:
    """
    Calculate the isothermal bulk modulus:

    :math:

       Bt = - V  \\left ( \\frac{ \\partial P }{ \\partial V } \\right )`

    :param v_vector: fine volume vector
    :param p_tv: pressure, :math:`P(T,V)`
    :return: isothermal bulk modulus, :math:`Bt(T,V)`
    """
    return -np.gradient(p_tv, axis=1) / np.gradient(v_vector) * v_vector


def adiabatic_bulk_modulus(bt_tp: Matrix, alpha_tp: Matrix, gamma_tp: Matrix, ts: Vector) -> Matrix:
    """
    Equation used to calculate adiabatic bulk modulus: :math:`Bs = Bt \\left ( 1 + \\alpha \\gamma T \\right )`

    :param bt_tp: isothermal bulk modulus, :math:`Bt(T,P)`
    :param alpha_tp: thermal expansion coefficient, :math:`\\alpha(T,P)`
    :param gamma_tp: thermodynamic gruneisen parameter, :math:`\\gamma(T,P)`
    :param ts: temperature vector
    :return: adiabatic bulk modulus, :math:`Bs(T,P)`
    """
    return bt_tp * (1.0 + alpha_tp * gamma_tp * ts[:, None])


def bulk_modulus_derivative(p_vector: Vector, bt_tp: Matrix) -> Matrix:
    """
    Equation used: :math:`Bt' = \\left ( \\frac{ \\partial Bt }{ \\partial P } \\right )`

    :param p_vector: desired pressure vector
    :param bt_tp: isothermal_bulk_modulus, :math:`Bt(T,P)`
    :return: :math:`Bt'(T,P)`
    """
    return calculate_derivatives(p_vector, bt_tp.T).T


def pressure_specific_heat_capacity(cv_tp: Matrix, alpha_tp: Matrix, gamma_tp: Matrix, ts: Vector) -> Matrix:
    """
    Equation used: :math:`Cp = Bt \\left ( 1 + \\alpha \\gamma T \\right )`

    :param cv_tp: volume specific heat capacity, :math:`Cv(T,P)`
    :param alpha_tp: thermal expansion coefficient, :math:`\\alpha(T,P)`
    :param gamma_tp: thermodynamic gruneisen parameter, :math:`\\gamma(T,P)`
    :param ts: temperature vector
    :return: pressure specific heat capacity, :math:`Cp(T,P)`
    """
    return cv_tp * (1.0 + alpha_tp * gamma_tp * ts[:, None])


def volume_specific_heat_capacity(ts: Vector, internal_energies: Matrix) -> Matrix:
    """
    Equation used: :math:`Cv = \\left ( \\frac{ \\partial U }{ \\partial T } \\right )`

    :param ts: temperature vector
    :param internal_energies: :math:`U(T,V)`
    :return: volume specific heat capacity, :math:`Cv(T,V)`
    """
    return calculate_derivatives(ts, internal_energies)
