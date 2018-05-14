#!/usr/bin/env python3
"""
:mod: bmf_all_t
================================

.. module bmf_all_t
   :platform: Unix, Windows, Mac, Linux
   :synopsis:
.. moduleauthor:: Tian Qin <qinxx197@umn.edu>
"""

from typing import Optional

import numpy as np
from numpy.linalg import inv

# ===================== What can be exported? =====================
__all__ = ['polynomial_least_square_fitting', 'polynomial_least_square_fitting_at_all_temperature']


def polynomial_least_square_fitting(x, y, new_x, order: Optional[int] = 3):
    """
    Equation of calculate the coefficients are from
    `Wolfram Mathworld <http://mathworld.wolfram.com/LeastSquaresFittingPolynomial.html>`_.

    :param x: Eulerian strain of calculated volumes (sparse)
    :param y: Free energy of these calculated volumes (sparse)
    :param new_x: Eulerian strain at a greater dense vector
    :param order: orders to fit Birch Murnaghan EOS
    :return: Free energy at a denser strain vector (denser volumes vector)
    """
    order += 1  # The order needed is 1 more than ``numpy.vander`` default value.
    X = np.vander(x, order, increasing=True)
    X_T = X.T
    a = inv(X_T @ X) @ X_T @ y
    new_y = np.vander(new_x, order, increasing=True) @ a
    return a, new_y


def polynomial_least_square_fitting_at_all_temperature(eulerian_strain, free_energy, strain, order: Optional[int] = 3):
    """
    Calculate the F(T,V) for given strain.

    :param eulerian_strain: Eulerian strain of calculated volumes (sparse)
    :param free_energy: Free energy of these calculated volumes (sparse)
    :param strain: Eulerian strain at a greater dense vector
    :param order: orders to fit Birch Murnaghan EOS
    :return: Free energy at a dense (T, V) grid.
    """
    temperature_amount, _ = free_energy.shape
    dense_volume_amount = len(strain)
    f_v_t = np.empty((temperature_amount, dense_volume_amount))  # Initialize the F(T,V) array

    for i in range(temperature_amount):
        _, f_i = polynomial_least_square_fitting(eulerian_strain, free_energy[i], strain, order)
        f_v_t[i] = f_i
    return f_v_t
