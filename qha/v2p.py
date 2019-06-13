#!/usr/bin/env python3
"""
.. module v2p
   :platform: Unix, Windows, Mac, Linux
   :synopsis:
.. moduleauthor:: Tian Qin <qinxx197@umn.edu>
.. moduleauthor:: Qi Zhang <qz2280@columbia.edu>
"""

import numba
import numpy as np

from qha.tools import vectorized_find_nearest
from qha.type_aliases import Matrix, Vector

# ===================== What can be exported? =====================
__all__ = ['v2p']


@numba.jit(nopython=True, parallel=True)
def _lagrange4(x: float, x0, x1, x2, x3, y0, y1, y2, y3) -> float:
    """
    A third-order Lagrange polynomial function. Given 4 points for interpolation:
    :math:`(x_0, y_0), \\ldots, (x_3, y_3)`, evaluate the Lagrange polynomial on :math:`x`.

    :param x: The x-coordinate of the point to be evaluated.
    :param x0: The x-coordinate of the 1st point.
    :param x1: The x-coordinate of the 2nd point.
    :param x2: The x-coordinate of the 3rd point.
    :param x3: The x-coordinate of the 4th point.
    :param y0: The y-coordinate of the 1st point.
    :param y1: The y-coordinate of the 2nd point.
    :param y2: The y-coordinate of the 3rd point.
    :param y3: The y-coordinate of the 4th point.
    :return: The y-coordinate of the point to be evaluated.
    """
    return (x - x1) * (x - x2) * (x - x3) / (x0 - x1) / (x0 - x2) / (x0 - x3) * y0 + \
           (x - x0) * (x - x2) * (x - x3) / (x1 - x0) / (x1 - x2) / (x1 - x3) * y1 + \
           (x - x0) * (x - x1) * (x - x3) / (x2 - x0) / (x2 - x1) / (x2 - x3) * y2 + \
           (x - x0) * (x - x1) * (x - x2) / (x3 - x0) / (x3 - x1) / (x3 - x2) * y3


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
    result = np.empty((t_amount, v_amount))

    extended_f = np.hstack((func_of_t_v[:, 3].reshape(-1, 1), func_of_t_v, func_of_t_v[:, -4].reshape(-1, 1)))
    extended_p = np.hstack((p_of_t_v[:, 3].reshape(-1, 1), p_of_t_v, p_of_t_v[:, -4].reshape(-1, 1)))

    desired_pressures_amount = len(desired_pressures)
    for i in range(t_amount):
        rs = np.zeros(desired_pressures_amount)
        vectorized_find_nearest(extended_p[i], desired_pressures, rs)

        for j in range(v_amount):
            k = int(rs[j])
            x1, x2, x3, x4 = extended_p[i, k - 1:k + 3]
            f1, f2, f3, f4 = extended_f[i, k - 1:k + 3]

            result[i, j] = _lagrange4(desired_pressures[j], x1, x2, x3, x4, f1, f2, f3, f4)
    return result
