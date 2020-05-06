#!/usr/bin/env python3
"""
.. module fitting
   :platform: Unix, Windows, Mac, Linux
   :synopsis: This module is one of the most important part of this package since it implements a robust
    finite strain EoS fitting for ``grid_interpolation`` module's use.
.. moduleauthor:: Tian Qin <qinxx197@umn.edu>
"""
import numpy as np

from qha.type_aliases import Matrix, Vector

# ===================== What can be exported? =====================
__all__ = ['apply_finite_strain_fitting']


def apply_finite_strain_fitting(strains_sparse: Vector, free_energies: Matrix, strains_dense: Vector,
                                order: int = 3):
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
        f_v_t[i] = np.poly1d(np.polyfit(strains_sparse, free_energies[i], order))(strains_dense)
    return f_v_t
