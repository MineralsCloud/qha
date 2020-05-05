#!/usr/bin/env python3
"""
.. module v2p
   :platform: Unix, Windows, Mac, Linux
   :synopsis:
.. moduleauthor:: Tian Qin <qinxx197@umn.edu>
.. moduleauthor:: Qi Zhang <qz2280@columbia.edu>
"""
import numpy as np
from scipy.interpolate import lagrange

from qha.tools import vectorized_find_nearest
from qha.type_aliases import Matrix, Vector

# ===================== What can be exported? =====================
__all__ = ['v2p']


def v2p(func_of_t_v: Matrix, p_of_t_v: Matrix, desired_pressures: Vector) -> Matrix:
    """
    Obtain :math:`f(T, P)` given :math:`f(T, V)` and :math:`P(T, V)` by doing a fourth-order Lagrangian interpolation.

    :param func_of_t_v: Any function :math:`f` on :math:`(T, V)` grid, which has
        shape: (number of temperature, number of volumes).
    :param p_of_t_v: Pressures on :math:`(T, V)` grid, which has
        shape: (number of temperature, number of volumes).
    :param desired_pressures: A vector of pressures which user wants to apply.
    :return: The interpolated function :math:`f` on :math:`(T, P)` grid.
    """
    t_amount, v_amount = func_of_t_v.shape
    desired_pressures_amount = len(desired_pressures)

    result = np.empty((t_amount, desired_pressures_amount))

    extended_f = np.hstack(
        (func_of_t_v[:, 3].reshape(-1, 1), func_of_t_v, func_of_t_v[:, -4].reshape(-1, 1)))
    extended_p = np.hstack(
        (p_of_t_v[:, 3].reshape(-1, 1), p_of_t_v, p_of_t_v[:, -4].reshape(-1, 1)))

    for i in range(t_amount):
        rs = np.zeros(desired_pressures_amount)
        vectorized_find_nearest(extended_p[i], desired_pressures, rs)

        for j in range(desired_pressures_amount):
            k = int(rs[j])
            # Potential bug: `lagrange` does not check whether there are 3 or 4 values
            result[i, j] = lagrange(extended_p[i, k - 1:k + 3], extended_f[i, k - 1:k + 3])(desired_pressures[j])
    return result
