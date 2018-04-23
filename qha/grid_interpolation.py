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

from qha.bmf import bmf, bmf_energy
from qha.type_aliases import Vector, Matrix
from qha.unit_conversion import gpa_to_ry_b3

# ===================== What can be exported? =====================
__all__ = ['calc_eulerian_strain', 'from_eulerian_strain', 'interpolate_volumes',
           'RefineGrid']


@vectorize([float64(float64, float64)], nopython=True)
def calc_eulerian_strain(v0, v):
    """

    :param v0: fixed
    :param v:
    :return:
    """
    return 1 / 2 * ((v0 / v) ** (2 / 3) - 1)


@vectorize([float64(float64, float64)], nopython=True)
def from_eulerian_strain(v0, s):
    """

    :param v0: fixed
    :param s:
    :return:
    """
    return v0 * (2 * s + 1) ** (-3 / 2)


@jit(UniTuple(float64[:], 2)(float64[:], int64, float64), nopython=True)
def interpolate_volumes(in_volumes, out_volumes_num, ratio):
    """
    For Eulerian strain, the larger the strain, the smaller the volume.
    So large volume corresponds to small strain.

    :param in_volumes:
    :param out_volumes_num:
    :param ratio:
    :return:
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

        :param volumes:
        :param free_energies:
        :param initial_ratio:
        :return:
        """
        strains, finer_volumes = interpolate_volumes(volumes, self.ntv, initial_ratio)
        eulerian_strain = calc_eulerian_strain(volumes[0], volumes)
        f_vt = bmf_energy(eulerian_strain, free_energies, len(volumes), strains, finer_volumes, self.ntv, self.option)
        p_vt = -np.gradient(f_vt) / np.gradient(finer_volumes)
        p_desire = gpa_to_ry_b3(self.p_desire)
        # find the index of the first pressure value that slightly smaller than p_desire
        idx = np.argmin(p_vt < p_desire)
        final_ratio = finer_volumes[idx] / max(volumes)
        return final_ratio

    def refine_grids(self, volumes: Vector, free_energies: Matrix,
                     ratio: Optional[float] = None) -> Tuple[Vector, Matrix, float]:
        """
        Get the appropriate volume grid for interpolation.
        Avoid to use a too large volume grid to obtain data, which might lose accuracy.

        :param free_energies: calculated Helmholtz Free Energies for different volumes
        :param volumes: on which volumes these calculations were perform.
        :param ratio:  this ratio is used to get a larger volume grid
        :return:
        """
        if ratio is not None:
            new_ratio: float = ratio
        else:
            new_ratio = self.approaching_to_best_ratio(volumes, free_energies[-1, :], 1.45)
            if new_ratio < 1.0:
                # if the new_ratio is smaller than 1.0, which means the volumes calculated is large enough,
                # there is no need to expand the volumes.
                new_ratio = 1.0

        nt = free_energies.shape[0]

        strains, finer_volumes = interpolate_volumes(volumes, self.ntv, new_ratio)
        f_vt = bmf(free_energies, volumes, strains, finer_volumes, self.ntv, nt, self.option)

        return finer_volumes, f_vt, new_ratio
