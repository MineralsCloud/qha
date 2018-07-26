#!/usr/bin/env python3
"""
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
    Equation used to calculate pressure: :math:`P = - \\left ( \\frac{ \\partial F }{ \\partial V } \\right )_T`

    :param v_vector: fine volumes vector
    :param free_energies: :math:`F(T,V)`
    :return: pressure, :math:`P(T,V)`
    """
    return -np.gradient(free_energies, axis=1) / np.gradient(v_vector)


def entropy(ts: Vector, free_energies: Matrix) -> Matrix:
    """
    Equation used to calculate entropy: :math:`S = - \\left ( \\frac{ \\partial F }{ \\partial T } \\right )_V`

    :param ts: temperature vector
    :param free_energies: :math:`F(T,V)`
    :return: entropy, :math:`S(T,V)`
    """
    return -calculate_derivatives(ts, free_energies)


def thermodynamic_potentials(ts: Vector, v_vector: Vector, free_energies: Matrix, p_tv: Matrix):
    """
    Calculate :math:`H`, :math:`U`, and :math:`G` on :math:`(T,V)` grid from :math:`F`;

    :math:`U = F + TS, H = U + PV, G = F + PV`

    input: nt, and F, which is Helmholtz Free Energy, are needed.


    :param free_energies: :math:`F(T,V)`
    :param p_tv: pressure, :math:`P(T,V)`
    :param ts: temperature vector
    :param v_vector: fine volumes vector
    :return: :math:`U`, :math:`H`, :math:`G` on :math:`(T,V)` grid
    """
    g: Matrix = free_energies + p_tv * v_vector  # G(T,V) = F(T,V) + V * P(T,V)

    u: Matrix = free_energies + entropy(ts, free_energies) * ts.reshape(-1, 1)  # U(T,V) = F(T,V) + T * S(T,V)

    h: Matrix = u + p_tv * v_vector  # H(T,V) = U(T,V) + V * P(T,V)

    return {'U': u, 'H': h, 'G': g}


def volume_tp(v_vector: Vector, p_vector: Vector, p_tv: Matrix) -> Matrix:
    """
    Convert volume as function of :math:`(T,P)`

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
    Thermal expansion: :math:`\\alpha = \\frac{ 1 }{ V }  \\left ( \\frac{ \\partial V }{ \\partial T } \\right )`

    :param ts: temperature vector
    :param v_tp: volume, :math:`V(T,P)`
    :return: thermal expansion coefficient, :math:`\\alpha(T,P)`
    """
    # Division is done by element-wise.
    return calculate_derivatives(ts, v_tp) / v_tp


def gruneisen_parameter(v_tp: Matrix, bt_tp: Matrix, alpha_tp: Matrix, cv_tp: Matrix) -> Matrix:
    """
    Equation used to calculate thermodynamic Gruneisen parameter: :math:`\\gamma = \\alpha B_{t} V / Cv`

    :param v_tp: volume, :math:`V(T,P)`
    :param bt_tp:isothermal bulk modulus :math:`Bt(T,P)`
    :param alpha_tp: thermal expansion coefficient, :math:`\\alpha(T,P)`
    :param cv_tp: volume specific heat capacity, :math:`Cv(T,P)`
    :return: thermodynamic gruneisen parameter, :math:`\\gamma(T,P)`
    """
    gamma = np.empty([v_tp.shape[0], v_tp.shape[1]])
    gamma[0] = 0.0
    gamma[1:, :] = v_tp[1:] * bt_tp[1:] * alpha_tp[1:] / cv_tp[1:]
    # return v_tp * bt_tp_au * alpha_tp / cv_tp_au
    return gamma


def isothermal_bulk_modulus(v_vector: Vector, p_tv: Matrix) -> Matrix:
    """
    Equation used to calculate isothermal bulk modulus: :math:`Bt = - V  \\left ( \\frac{ \\partial P }{ \\partial V } \\right )`

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


def pressure_specific_heat_capacity(ts: Vector, h_tp: Matrix) -> Matrix:
    """
    Equation used: :math:`Cp = \\frac{ \\partial H }{ \\partial T }`

    :param ts: temperature vector
    :param h_tp: enthalpy :math:`H(T,P)`
    :return: pressure specific heat capacity, :math:`Cp(T,P)`
    """
    return calculate_derivatives(ts, h_tp)

def volume_specific_heat_capacity(ts: Vector, internal_energies: Matrix) -> Matrix:
    """
    Equation used: :math:`Cv = \\left ( \\frac{ \\partial U }{ \\partial T } \\right )`

    :param ts: temperature vector
    :param internal_energies: :math:`U(T,V)`
    :return: volume specific heat capacity, :math:`Cv(T,V)`
    """
    return calculate_derivatives(ts, internal_energies)
