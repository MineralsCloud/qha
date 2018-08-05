#!/usr/bin/env python3
"""
.. module grid_interpolation
   :platform: Unix, Windows, Mac, Linux
   :synopsis: This module defines a class ``FinerGrid`` that will do Birch--Murnaghan EoS fitting on the input
    free energies and volumes, and evaluate the fitted function on a denser volume grid.
.. moduleauthor:: Tian Qin <qinxx197@umn.edu>
.. moduleauthor:: Qi Zhang <qz2280@columbia.edu>
"""

from typing import Optional, Tuple

import numpy as np
from numba import vectorize, float64

from qha.fitting import polynomial_least_square_fitting, birch_murnaghan_finite_strain_fitting
from qha.type_aliases import Vector, Matrix
from qha.unit_conversion import gpa_to_ry_b3

# ===================== What can be exported? =====================
__all__ = [
    'calculate_eulerian_strain',
    'from_eulerian_strain',
    'VolumesExpander',
    'FinerGrid'
]


@vectorize([float64(float64, float64)], nopython=True)
def calculate_eulerian_strain(v0, v):
    """
    Calculate Eulerian strain (:math:`f`) of a given volume vector *v* regarding as a reference volume *v0*, where

    .. math::

       f = \\frac{ 1 }{ 2 } \\bigg( \\Big( \\frac{ V_0 }{ V }^{2/3} \\Big) -1 \\bigg).

    :param v0: The volume set as the reference for the Eulerian strain calculation.
    :param v: A volume vector, whose each item will be calculated Eulerian strain with respect to *v0*.
    :return: A vector which contains the calculated Eulerian strain.
    """
    return 1 / 2 * ((v0 / v) ** (2 / 3) - 1)


@vectorize([float64(float64, float64)], nopython=True)
def from_eulerian_strain(v0, f):
    """
    Calculate the corresponding volumes :math:`V` from a vector of given Eulerian strains (*f*)
    and a reference volume *v0*. It is the inverse function of the ``calc_eulerian_strain`` function, i.e.,

    .. math::

       V = V_0 (2 f + 1)^{-3/2}.

    :param v0: The volume set as a reference for volume calculation, i.e., :math:`V_0` mentioned above.
    :param f: A vector of Eulerian strains with respect to :math:`V_0`.
    :return: A vector of calculated volume :math:`V`.
    """
    return v0 * (2 * f + 1) ** (-3 / 2)


class VolumesExpander:
    """
    Interpolate volumes on input volumes *in_volumes*, with *ratio* given.
    For Eulerian strain, the larger the strain, the smaller the volume.
    So larger volume corresponds to smaller strain.

    Algorithm:

       1. Find the maximum and minimum volumes of *in_volumes*.
       2. Expand the lower and upper boundaries of the volumes to :math:`V_\text{lower}` and :math:`V_\text{upper})`
          by :math:`V_\text{lower} = \frac{ V_\text{min} }{ r }` and :math:`V_\text{upper} = V_\text{max} r`, where
          :math:`r` is the *ratio*, which is usually an empirical parameter.
       3. The Eulerian strains of :math:`V_\text{lower}` and :math:`V_\text{upper}` with respect to :math:`V_\text{max}`
          is calculated. Then a linear sequence between the lower and upper boundaries of the strains is generated.
          It is the ``strains`` attribute.
       4. The volumes corresponding to ``strains`` are generated by function ``from_eulerian_strain``.

    **Note:** To use this class, the method ``interpolate_volumes`` must be called immediately after
    instantiating it. Otherwise, the ``strains`` and ``out_volumes`` attributes are all ``None``, which is usually not
    expected.

    :param in_volumes: An input vector of volumes.
    :param out_volumes_num: Number of output volumes. It should be larger than the number of input volumes.
    :param ratio: The ratio of the upper boundary of expanded volumes with respect to the largest input volume in
        *in_volumes*. An empirical parameter, better lower than ``1.5``. Otherwise, the result may not be reliable.
    """

    def __init__(self, in_volumes: Vector, out_volumes_num: int, ratio: float):
        self._in_volumes = np.array(in_volumes, dtype=float)
        self._out_volumes_num = int(out_volumes_num)
        self._ratio = float(ratio)
        self._strains = None
        self._out_volumes = None

    @property
    def in_volumes(self):
        return self._in_volumes

    @property
    def ratio(self) -> float:
        return self._ratio

    @ratio.setter
    def ratio(self, value: float):
        self._ratio = float(value)

    @property
    def out_volumes_num(self) -> int:
        return self._out_volumes_num

    @out_volumes_num.setter
    def out_volumes_num(self, value: int):
        if not isinstance(value, int):
            raise TypeError("The argument *out_volumes_num* must be an integer!")
        if value <= 0:
            raise ValueError("The argument *out_volumes_num* must be an integer larger than 0!")
        self._out_volumes_num = value

    @property
    def strains(self) -> Optional[Vector]:
        return self._strains

    @property
    def out_volumes(self) -> Optional[Vector]:
        return self._out_volumes

    def interpolate_volumes(self) -> None:
        v_min, v_max = np.min(self._in_volumes), np.max(self._in_volumes)
        # :math:``r = v_upper / v_max = v_min / v_lower``
        v_lower, v_upper = v_min / self._ratio, v_max * self._ratio
        # The *v_max* is a reference value here.
        s_upper, s_lower = calculate_eulerian_strain(v_max, v_lower), calculate_eulerian_strain(v_max, v_upper)
        self._strains = np.linspace(s_lower, s_upper, self._out_volumes_num)
        self._out_volumes = from_eulerian_strain(v_max, self._strains)


class FinerGrid:
    """
    A class that will do the Birch--Murnaghan finite-strain EoS fitting,
    and evaluate the fitted function on a denser volume grid.

    :param desired_p_min: The desired minimum pressure to calculate for further steps.
    :param nv: The number of volumes on a denser grid.
    :param order: The order of the Birch--Murnaghan finite-strain EoS fitting.
    """

    def __init__(self, desired_p_min: float, nv: int, order: Optional[int] = 3):
        self.p_desire = float(desired_p_min)
        self.dense_volumes_amount = int(nv)
        self.option = int(order)

    def approach_to_best_ratio(self, volumes: Vector, free_energies: Vector, initial_ratio: float) -> float:
        """
        Trying to find the best volume grids based on an a very large volume grids.

        :param volumes: Volumes of these calculations were perform (sparse).
        :param free_energies: Free energies at the highest temperature (sparse).
        :param initial_ratio: Initial ratio, a guess value, which can be set to a very large number.
        :return: The suitable `ratio` for further calculation.
        """
        vr = VolumesExpander(volumes, self.dense_volumes_amount, initial_ratio)
        vr.interpolate_volumes()
        strains, finer_volumes = vr.strains, vr.out_volumes
        eulerian_strain = calculate_eulerian_strain(volumes[0], volumes)
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

        eulerian_strain = calculate_eulerian_strain(volumes[0], volumes)
        vr = VolumesExpander(volumes, self.dense_volumes_amount, new_ratio)
        vr.interpolate_volumes()
        strains, finer_volumes = vr.strains, vr.out_volumes
        f_tv_bfm = birch_murnaghan_finite_strain_fitting(eulerian_strain, free_energies, strains, self.option)
        return finer_volumes, f_tv_bfm, new_ratio
