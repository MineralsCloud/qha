#!/usr/bin/env python3
"""
.. module fitting
   :platform: Unix, Windows, Mac, Linux
   :synopsis: This module is one of the most important part of this package since it implements a robust
    Birch--Murnaghan EoS fitting for ``grid_interpolation`` modules' use.
.. moduleauthor:: Tian Qin <qinxx197@umn.edu>
"""

from typing import Optional

import numpy as np
from numpy.linalg import inv

# ===================== What can be exported? =====================
__all__ = ['polynomial_least_square_fitting', 'birch_murnaghan_finite_strain_fitting']


def polynomial_least_square_fitting(x, y, new_x, order: Optional[int] = 3):
    """
    Free Energy is expanded to the ``order``:math:`^\mathrm{th}` order in strain.

    Check the `Wolfram Mathworld <http://mathworld.wolfram.com/LeastSquaresFittingPolynomial.html>`_
    to find the method of calculating the coefficients.

    :param x: Eulerian strain of calculated volumes (sparse).
    :param y: Free energy of these calculated volumes (sparse).
    :param new_x: Eulerian strain at a greater dense vector.
    :param order: The order chose to fit Birch--Murnaghan EoS, default is ``3``, i.e., third-order Birch--Murnaghan
        EoS fitting.
    :return: Free energy at a denser strain vector (denser volumes vector).
    """
    order += 1  # The order needed is 1 more than ``numpy.vander`` default value.
    X = np.vander(x, order, increasing=True)  # This will make a Vandermonde matrix that will be used in BM fitting.
    X_T = X.T
    a = inv(X_T @ X) @ X_T @ y
    new_y = np.vander(new_x, order, increasing=True) @ a
    return a, new_y


def birch_murnaghan_finite_strain_fitting(eulerian_strain, free_energy, strain, order: Optional[int] = 3):
    """
    Calculate the ``F(T, V)`` for given strain.
    Free Energy is expanded to the ``order``:math:`^\mathrm{th}` order in strain.

    :param eulerian_strain: Eulerian strain of calculated volumes (sparse).
    :param free_energy: Free energy of these calculated volumes (sparse).
    :param strain: Eulerian strain at a greater dense vector.
    :param order: The order chose to fit Birch--Murnaghan EoS, default is ``3``, i.e., third-order Birch--Murnaghan
        EoS fitting.
    :return: Free energy at a dense :math:`(T, V)` grid.
    """
    temperature_amount, _ = free_energy.shape
    dense_volume_amount = len(strain)
    f_v_t = np.empty((temperature_amount, dense_volume_amount))  # Initialize the F(T,V) array

    for i in range(temperature_amount):
        _, f_i = polynomial_least_square_fitting(eulerian_strain, free_energy[i], strain, order)
        f_v_t[i] = f_i
    return f_v_t
