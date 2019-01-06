#!/usr/bin/env python3
"""
.. module fitting
   :platform: Unix, Windows, Mac, Linux
   :synopsis: This module is one of the most important part of this package since it implements a robust
    finite strain EoS fitting for ``grid_interpolation`` module's use.
.. moduleauthor:: Tian Qin <qinxx197@umn.edu>
"""

from typing import Optional

import numpy as np
from numpy.linalg import inv
from qha.type_aliases import Matrix, Vector

# ===================== What can be exported? =====================
__all__ = ['polynomial_least_square_fitting', 'apply_finite_strain_fitting']


def polynomial_least_square_fitting(xs, ys, new_xs, order: Optional[int] = 3):
    """
    The algorithm is referenced from the
    `Wolfram MathWorld <http://mathworld.wolfram.com/LeastSquaresFittingPolynomial.html>`_.

    :param xs: A vector of existing x-coordinates.
    :param ys: A vector of y-coordinates correspond to the *xs*.
    :param new_xs: A new vector of x-coordinates to be applied with the polynomial-fitting result.
    :param order: The order chose to fit the finite strain EoS, the default value is ``3``,
        which is, the third-order Birch--Murnaghan EoS.
    :return: A tuple, the polynomial-fitting coefficients and the new vector of y-coordinates.
    """
    order += 1  # The definition of order in ``numpy.vander`` is different from the order in finite strain by one.
    xx = np.vander(xs, order, increasing=True)  # This will make a Vandermonde matrix that will be used in EoS fitting.
    xx_t = xx.T  # Transpose the matrix.
    a = inv(xx_t @ xx) @ xx_t @ ys  # a = (X^T . X)^{-1} . X^T . ys
    new_y = np.vander(new_xs, order, increasing=True) @ a
    return a, new_y


def apply_finite_strain_fitting(strains_sparse: Vector, free_energies: Matrix, strains_dense: Vector,
                                order: Optional[int] = 3):
    """
    Calculate the free energies :math:`F(T, V)` for some strains (*strains_dense*), with the
    free energies (*free_energies*) on some other strains (*strains_sparse*) known already.
    Do a polynomial curve-fitting the apply the fitted function
    to the *strains_dense*.

    :param strains_sparse: A vector of the Eulerian strains for a sparse set of volumes.
    :param free_energies: The free energies correspond to *strains_sparse* at several temperature.
    :param strains_dense: A vector of the Eulerian strains at a denser set of volumes.
    :param order: The order chose to fit the finite strain EoS, the default value is ``3``,
        which is, the third-order Birch--Murnaghan EoS.
    :return: The free energies correspond to *strains_dense* at different temperature.
    """
    temperature_amount, _ = free_energies.shape
    dense_volume_amount = len(strains_dense)
    f_v_t = np.empty((temperature_amount, dense_volume_amount))  # Initialize the F(T,V) array

    for i in range(temperature_amount):
        _, f_i = polynomial_least_square_fitting(strains_sparse, free_energies[i], strains_dense, order)
        f_v_t[i] = f_i
    return f_v_t
