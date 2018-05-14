#!/usr/bin/env python3
"""
:mod:`` --
========================================

.. module
   :platform: Unix, Windows, Mac, Linux
   :synopsis:
.. moduleauthor:: Tian Qin <qinxx197@umn.edu>
.. moduleauthor:: Qi Zhang <qz2280@columbia.edu>
"""

from typing import Optional, Tuple

import numpy as np
from numba import vectorize, float64, jit, int64
from numba.types import UniTuple

from qha.bmf import polynomial_least_square_fitting, polynomial_least_square_fitting_at_all_temperature
from qha.type_aliases import Vector, Matrix
from qha.unit_conversion import gpa_to_ry_b3

# ===================== What can be exported? =====================
__all__ = ['calc_eulerian_strain', 'from_eulerian_strain', 'interpolate_volumes',
           'RefineGrid']


@vectorize([float64(float64, float64)], nopython=True)
def calc_eulerian_strain(v0, v):
    """
    Calculate Eulerian strain (`f`)  of a given volume vector `v` regarding to a reference `v0`,
    f = 1 / 2 * ((v0 / v) ** (2 / 3) - 1)
    :param v0: reference volume `v0`
    :param v: the given volume vector
    :return: a vector of calculated eulerian strain.
    """
    return 1 / 2 * ((v0 / v) ** (2 / 3) - 1)


@vectorize([float64(float64, float64)], nopython=True)
def from_eulerian_strain(v0, f):
    """
    Calculate volume from given Eulerian strain (`f`) and reference volume `v0`
    :param v0: Reference volume `v0`
    :param f: Eulerian strain
    :return: calculated volume
    """
    return v0 * (2 * f + 1) ** (-3 / 2)


@jit(UniTuple(float64[:], 2)(float64[:], int64, float64), nopython=True)
def interpolate_volumes(in_volumes, out_volumes_num, ratio):
    """
    For Eulerian strain, the larger the strain, the smaller the volume.
    So large volume corresponds to small strain.
    :param in_volumes: input volume vector
    :param out_volumes_num: numbers of output volumes
    :param ratio: The ratio of the largest volume used in fitting to the largest input volumes .
    :return: strains in a finer vector, and volumes at a finer vector.
    """
    v_min, v_max = np.min(in_volumes), np.max(in_volumes)
    v_smallest, v_largest = v_min / ratio, v_max * ratio
    # The *v_max* is a reference value here. It equals to ``v_max / v_largest = v_smallest / v_min``.
    s_largest, s_smallest = calc_eulerian_strain(v_max, v_smallest), calc_eulerian_strain(v_max, v_largest)
    strains = np.linspace(s_smallest, s_largest, out_volumes_num)
    return strains, from_eulerian_strain(v_max, strains)


class RefineGrid:
    def __init__(self, p_desire: float, nv: int, eos_name: Optional[str] = 'b-m', option: Optional[int] = 3):
        self.p_desire = p_desire
        self.eos_name = eos_name
        self.ntv = int(nv)
        self.option = option

    def approaching_to_best_ratio(self, volumes: Vector, free_energies: Vector, initial_ratio: float) -> float:
        """
        Trying to find the best volume grids based on an a very large volume grids.
        :param volumes: Volumes of these calculations were perform (sparse).
        :param free_energies: Free energies at the highest temperature (sparse).
        :param initial_ratio: Initial ratio, a guess value, which can be set to a very large number.
        :return: The suitable `ratio` for further calculation.
        """
        strains, finer_volumes = interpolate_volumes(volumes, self.ntv, initial_ratio)
        eulerian_strain = calc_eulerian_strain(volumes[0], volumes)
        _, f_v_tmax = polynomial_least_square_fitting(eulerian_strain, free_energies, strains, self.option)
        p_v_tmax = -np.gradient(f_v_tmax) / np.gradient(finer_volumes)
        p_desire = gpa_to_ry_b3(self.p_desire)
        # find the index of the first pressure value that slightly smaller than p_desire
        idx = np.argmin(p_v_tmax < p_desire)
        final_ratio = finer_volumes[idx] / max(volumes)
        return final_ratio

    def refine_grids(self, volumes: Vector, free_energies: Matrix,
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
            new_ratio = self.approaching_to_best_ratio(volumes, free_energies[-1, :], 1.45)
            if new_ratio < 1.0:
                # if the new_ratio is smaller than 1.0, which means the volumes calculated is large enough,
                # there is no need to expand the volumes.
                new_ratio = 1.0

        eulerian_strain = calc_eulerian_strain(volumes[0], volumes)
        strains, finer_volumes = interpolate_volumes(volumes, self.ntv, new_ratio)
        # f_tv = bmf_all_t(eulerian_strain, free_energies, strains, self.option)
        f_tv_bfm = polynomial_least_square_fitting_at_all_temperature(eulerian_strain, free_energies, strains, self.option)
        return finer_volumes, f_tv_bfm, new_ratio
        # return finer_volumes, f_tv, new_ratio
