#!/usr/bin/env python3
"""
.. module
   :platform: Unix, Windows, Mac, Linux
   :synopsis: This module defines a class ``RefineGrid`` that will do Birch--Murnaghan EoS fitting on the input
    free energies and volumes, and evaluate the fitted function on a denser volume grid.
.. moduleauthor:: Tian Qin <qinxx197@umn.edu>
.. moduleauthor:: Qi Zhang <qz2280@columbia.edu>
"""

from typing import Optional, Tuple

import numpy as np
from numba import vectorize, float64, jit, int64
from numba.types import UniTuple

from qha.fitting import polynomial_least_square_fitting, birch_murnaghan_finite_strain_fitting
from qha.type_aliases import Vector, Matrix
from qha.utils.unit_conversion import gpa_to_ry_b3

# ===================== What can be exported? =====================
__all__ = ['calc_eulerian_strain', 'from_eulerian_strain', 'interpolate_volumes',
           'RefineGrid']


@vectorize([float64(float64, float64)], nopython=True)
def calc_eulerian_strain(v0, v):
    """
    Calculate Eulerian strain (:math:`f`) of a given volume vector *v* regarding to a reference *v0*, where

    .. math::

        f = \\frac{ 1 }{ 2 } \\bigg( \\Big( \\frac{ V_0 }{ V }^{2/3} \\Big) -1 \\bigg).

    :param v0: The volume set as reference for Eulerian strain calculation.
    :param v: The volume to be calculated its strain W.R.T. *v0*.
    :return: Calculated Eulerian strain.
    """
    return 1 / 2 * ((v0 / v) ** (2 / 3) - 1)


@vectorize([float64(float64, float64)], nopython=True)
def from_eulerian_strain(v0, f):
    """
    Calculate corresponding volume :math:`V` from given Eulerian strain (*f*) and reference volume *v0*. It is the
    inverse of ``calc_eulerian_strain`` function, i.e.,

    .. math::

        V = V_0 (2 f + 1)^{-3/2}.

    :param v0: The volume set as reference for volume calculation.
    :param f: Eulerian strain for :math:`V` W.R.T. :math:`V_0`.
    :return: Calculated volume :math:`V`.
    """
    return v0 * (2 * f + 1) ** (-3 / 2)


@jit(UniTuple(float64[:], 2)(float64[:], int64, float64), nopython=True)
def interpolate_volumes(in_volumes, out_volumes_num, ratio):
    """
    Interpolate volumes on input, with *ratio* given.
    For Eulerian strain, the larger the strain, the smaller the volume. So large volume corresponds to small strain.

    :param in_volumes: The input sparse 1D array of volumes.
    :param out_volumes_num: Number of output volumes. It should be larger than the number of input volumes.
    :param ratio: The ratio of the largest volume used in fitting W.R.T. the largest input volumes.
    :return: The interpolated strains in a finer grid, and corresponding volumes.
    """
    v_min, v_max = np.min(in_volumes), np.max(in_volumes)
    v_smallest, v_largest = v_min / ratio, v_max * ratio
    # The *v_max* is a reference value here. It equals to ``v_max / v_largest = v_smallest / v_min``.
    s_largest, s_smallest = calc_eulerian_strain(v_max, v_smallest), calc_eulerian_strain(v_max, v_largest)
    strains = np.linspace(s_smallest, s_largest, out_volumes_num)
    return strains, from_eulerian_strain(v_max, strains)


class RefineGrid:
    """
    A class that will do the Birch--Murnaghan finite-strain EoS fitting,
    and evaluate the fitted function on a denser volume grid.

    :param desired_p_min: The desired minimum pressure to calculate for further steps.
    :param nv: The number of volumes on a denser grid.
    :param order: The order of the Birch--Murnaghan finite-strain EoS fitting.
    """

    def __init__(self, desired_p_min: float, nv: int, order: Optional[int] = 3):
        self.p_desire = desired_p_min
        self.dense_volumes_amount = int(nv)
        self.option = order

    def approach_to_best_ratio(self, volumes: Vector, free_energies: Vector, initial_ratio: float) -> float:
        """
        Trying to find the best volume grids based on an a very large volume grids.

        :param volumes: Volumes of these calculations were perform (sparse).
        :param free_energies: Free energies at the highest temperature (sparse).
        :param initial_ratio: Initial ratio, a guess value, which can be set to a very large number.
        :return: The suitable `ratio` for further calculation.
        """
        strains, finer_volumes = interpolate_volumes(volumes, self.dense_volumes_amount, initial_ratio)
        eulerian_strain = calc_eulerian_strain(volumes[0], volumes)
        _, f_v_tmax = polynomial_least_square_fitting(eulerian_strain, free_energies, strains, self.option)
        p_v_tmax = -np.gradient(f_v_tmax) / np.gradient(finer_volumes)
        p_desire = gpa_to_ry_b3(self.p_desire)
        # Find the index of the first pressure value that slightly smaller than p_desire.
        idx = np.argmin(p_v_tmax < p_desire)
        final_ratio = finer_volumes[idx] / max(volumes)
        return final_ratio

    def refine_grid(self, volumes: Vector, free_energies: Matrix,
                    ratio: Optional[float] = None) -> Tuple[Vector, Matrix, float]:
        """
        Get the appropriate volume grid for interpolation.
        Avoid to use a too large volume grid to obtain data, which might lose accuracy.

        :param free_energies: Calculated Helmholtz Free Energies for input volumes (sparse).
        :param volumes: Volumes of these calculations were perform (sparse).
        :param ratio: This ratio is used to get a larger volume grid
        :return: volume, Helmholtz free energy at a denser vector, and the `ratio` used in this calculation
        """
        if ratio is not None:
            new_ratio: float = ratio
        else:
            new_ratio = self.approach_to_best_ratio(volumes, free_energies[-1, :], 1.45)
            if new_ratio < 1.0:
                # if the new_ratio is smaller than 1.0, which means the volumes calculated is large enough,
                # there is no need to expand the volumes.
                new_ratio = 1.0

        eulerian_strain = calc_eulerian_strain(volumes[0], volumes)
        strains, finer_volumes = interpolate_volumes(volumes, self.dense_volumes_amount, new_ratio)
        f_tv_bfm = birch_murnaghan_finite_strain_fitting(eulerian_strain, free_energies, strains, self.option)
        return finer_volumes, f_tv_bfm, new_ratio
