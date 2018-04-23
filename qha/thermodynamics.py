#!/usr/bin/env python3
"""
:mod:`thermodynamics` -- title
========================================

.. module thermodynamics
   :platform: Unix, Windows, Mac, Linux
   :synopsis: Calculate the basic thermodynamics for system: S, U, H, G, Cv on a (T,V) grid.
.. moduleauthor:: Tian Qin <qinxx197@umn.edu>
.. moduleauthor:: Qi Zhang <qz2280@columbia.edu>
"""

import numpy as np

from qha.type_aliases import Matrix, Vector
from qha.v2p import v2p

# ===================== What can be exported? =====================
__all__ = [
    'pressure_tv',
    'entropy',
    'thermodynamic_potentials',
    'volume_tp',
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
    Derivative of :math:`\\frac{ df(x) }{ dx }`.
    :param xs: 1D vector, of length nx.
    :param fs: 2D matrix, of shape (nx, _).
    :return: 2D matrix, of shape (nx, _).
    """
    if xs.ndim > 1 or fs.ndim < 2:
        raise ValueError('*xs* should be one-dimensional array and *ys* should be two-dimensional array!')

    return np.gradient(fs, axis=0) / np.gradient(xs)[:, None]  # df(x)/dx.


def pressure_tv(v_vector: Vector, free_energies: Matrix) -> Matrix:
    """
    P = -dF / dV |_T
    :param v_vector: fine volumes vector
    :param free_energies: F(T,V)
    :return: pressure, P(T,V)
    """
    return -np.gradient(free_energies, axis=1) / np.gradient(v_vector)


def entropy(ts: Vector, free_energies: Matrix) -> Matrix:
    """
    S= -dF / dT |_V
    :param ts: temperature vector
    :param free_energies: F(T,V)
    :return: entropy, S(T,V)
    """
    return -calculate_derivatives(ts, free_energies)


def thermodynamic_potentials(ts: Vector, v_vector: Vector, free_energies: Matrix, p_tv: Matrix):
    """
    Calculate H, U, and G on (T,V) grid from F;
    input: nt, and F, which is Helmholtz Free Energy, are needed
    U = F + T * S
    H = U + V * P
    G = F + V * P
    :param free_energies: F(T,V)
    :param p_tv: pressure, P(T,V)
    :param ts: temperature vector
    :param v_vector: fine volumes vector
    :return: U, H, G on (T,V) grid
    """
    g: Matrix = free_energies + p_tv * v_vector  # G(T,V) = F(T,V) + V * P(T,V)

    u: Matrix = free_energies + entropy(ts, free_energies) * ts.reshape(-1, 1)  # U(T,V) = F(T,V) + T * S(T,V)

    h: Matrix = u + p_tv * v_vector  # H(T,V) = U(T,V) + V * P(T,V)

    return {'U': u, 'H': h, 'G': g}


def volume_tp(v_vector: Vector, p_vector: Vector, p_tv: Matrix) -> Matrix:
    """
    Convert volume as function of (T,P)
    :param v_vector: fine volumes vector
    :param p_vector: desired pressure vector
    :param p_tv: P(T,V) in au.
    :return: volume, V(T,P)
    """
    nt, ntv = p_tv.shape
    v_tv = v_vector.reshape(1, -1).repeat(nt, axis=0)
    v_tp = v2p(v_tv, p_tv, p_vector)
    return v_tp


def thermal_expansion_coefficient(ts: Vector, v_tp: Matrix) -> Matrix:
    """
    alpha = 1 / V * (dV / dT)
    :param ts: temperature vector
    :param v_tp: volume, V(T,P)
    :return: thermal expansion coefficient, alpha(T,P)
    """
    # Division is done by element-wise.
    return calculate_derivatives(ts, v_tp) / v_tp


def gruneisen_parameter(v_tp: Matrix, bt_tp: Matrix, alpha_tp: Matrix, cv_tp: Matrix) -> Matrix:
    """
    gamma = alpha  * Bt  * V  / Cv
    :param v_tp: volume, V(T,P)
    :param bt_tp: isothermal_bulk_moduli(T,P)
    :param alpha_tp: thermal_expansion_coefficient(T,P)
    :param cv_tp: volume_specific_heat_capacity(T,P)
    :return: thermodynamic gruneisen parameter, gamma(T,P)
    """
    gamma = np.empty([v_tp.shape[0], v_tp.shape[1]])
    gamma[0] = 0.0
    gamma[1:, :] = v_tp[1:] * bt_tp[1:] * alpha_tp[1:] / cv_tp[1:]
    # return v_tp * bt_tp_au * alpha_tp / cv_tp_au
    return gamma


def isothermal_bulk_modulus(v_vector: Vector, p_tv: Matrix) -> Matrix:
    """
    bt = -V * dP / dV
    :param v_vector: fine volume vector
    :param p_tv: pressure, P(T,V)
    :return: isothermal bulk modulus, Bt(T,V)
    """
    return -np.gradient(p_tv, axis=1) / np.gradient(v_vector) * v_vector


def adiabatic_bulk_modulus(bt_tp: Matrix, alpha_tp: Matrix, gamma_tp: Matrix, ts: Vector) -> Matrix:
    """
    Bs = Bt * (1 + alpha * gamma_tp * T)
    :param bt_tp: isothermal bulk modulus, Bt(T,P)
    :param alpha_tp: thermal expansion coefficient, alpha(T,P)
    :param gamma_tp: thermodynamic gruneisen parameter, gamma(T,P)
    :param ts: temperature vector
    :return: adiabatic bulk modulus, Bs(T,P)
    """
    return bt_tp * (1.0 + alpha_tp * gamma_tp * ts[:, None])


def bulk_modulus_derivative(p_vector: Vector, bt_tp: Matrix) -> Matrix:
    """
    B'= dB / dP
    :param p_vector: desired pressure vector
    :param bt_tp: isothermal_bulk_modulus, Bt(T,P)
    :return: B', Bpt(T,P)
    """
    return calculate_derivatives(p_vector, bt_tp.T).T


def pressure_specific_heat_capacity(cv_tp: Matrix, alpha_tp: Matrix, gamma_tp: Matrix, ts: Vector) -> Matrix:
    """
    Cp= Bt * (1 + alpha * gamma_tp * T)
    :param cv_tp: volume specific heat capacity, Cv(T,P)
    :param alpha_tp: thermal expansion coefficient, alpha(T,P)
    :param gamma_tp: thermodynamic gruneisen parameter, gamma(T,P)
    :param ts: temperature vector
    :return: pressure specific heat capacity, Cp(T,P)
    """
    return cv_tp * (1.0 + alpha_tp * gamma_tp * ts[:, None])


def volume_specific_heat_capacity(ts: Vector, internal_energies: Matrix) -> Matrix:
    """
    Cv =dU/dT
    :param ts: temperature vector
    :param internal_energies: U(T,V)
    :return: volume specific heat capacity, Cv(T,V)
    """
    return calculate_derivatives(ts, internal_energies)
