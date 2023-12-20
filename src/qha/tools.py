#!/usr/bin/env python3
"""
.. module tools
   :platform: Unix, Windows, Mac, Linux
   :synopsis: This module defines some tools used in this package.
.. moduleauthor:: Qi Zhang <qz2280@columbia.edu>
.. moduleauthor:: Tian Qin <qinxx197@umn.edu>
"""

from typing import Callable, Optional

import numpy as np
from numba import float64, int64, void, vectorize, guvectorize, jit

from qha.fitting import polynomial_least_square_fitting
from qha.grid_interpolation import calculate_eulerian_strain
from qha.type_aliases import Matrix, Scalar, Vector

# ===================== What can be exported? =====================
__all__ = [
    "vectorized_find_nearest",
    "is_monotonic_decreasing",
    "arange",
    "calibrate_energy_on_reference",
]


@guvectorize(
    [void(float64[:], float64[:], int64[:])], "(m),(n)->(n)", nopython=True, cache=True
)
def vectorized_find_nearest(array: Vector, values: Vector, result: Vector):
    """
    A vectorized version of function ``find_nearest``.

    :param array: An array of monotonic increasing real numbers.
    :param values: An array of values, each of which is one between two of the consecutive elements in *array*.
    :param result: An array of indices. It is suggested to generate a vector of zeros by ``numpy`` package.
    :return: The *result*, an array of indices mentioned above.
    """
    n: int = len(array)

    if len(values) != len(result):
        raise ValueError("The *values* and *result* arguments should have same length!")

    for i in range(len(values)):
        if values[i] <= array[0]:
            result[i] = 0
        elif values[i] >= array[-1]:
            result[i] = n - 2

        j_low = 0  # Initialize lower limit.
        j_up = n - 1  # Initialize upper limit.

        while j_up - j_low > 1:  # If we are not yet done,
            j_mid: int = (j_up + j_low) // 2  # compute a midpoint,
            if values[i] >= array[j_mid]:
                j_low = j_mid  # and replace either the lower limit
            else:
                j_up = j_mid  # or the upper limit, as appropriate.
            # Repeat until the test condition is satisfied.

        result[i] = j_low


def arange(start: Scalar, num: int, step: Scalar) -> Vector:
    """
    Similar to ``numpy.arange``, generate an one-dimensional array but with *start*, *num*, *step* specified.

    :param start: The starting point of the array, which is included in this array.
    :param num: The total number of elements in this array.
    :param step: A number specifying the difference between any of the two elements.
    :return: An arithmetic progression.
    """
    return np.array([start + step * n for n in range(int(num))])


def is_monotonic_decreasing(array: Vector) -> bool:
    """
    Check whether the *array* is monotonic decreasing or not.
    For example, in QHA calculation, the volumes should be listed as a decreasing array,
    while the pressures should be monotonic increasing.
    This function can be used to check whether the volumes are in the right order.

    .. doctest::

        >>> is_monotonic_decreasing([1, 2, 4, 5, 9])
        False
        >>> is_monotonic_decreasing([2, -5, -10, -20])
        True

    :param array: The array to be evaluated.
    :return: ``True`` if the argument *array* is monotonic decreasing, otherwise ``False``.
    """
    dx = np.diff(array)
    return np.all(dx <= 0)


def calibrate_energy_on_reference(
    volumes_before_calibration: Matrix,
    energies_before_calibration: Matrix,
    order: Optional[int] = 3,
):
    """
    In multi-configuration system calculation, the volume set of each calculation may vary a little,
    This function would make the volume set of the first configuration (normally, the most populated configuration)
    as a reference volume set, then calibrate the energies of all configurations to this reference volume set.

    :param volumes_before_calibration: Original volume sets of all configurations
    :param energies_before_calibration: Free energies of all configurations on the original volume sets.
    :param order: The order of Birch--Murnaghan EOS fitting.
    :return: Free energies of each configuration on the
        referenced volumes (usually the volumes of the first configuration).
    """
    configurations_amount, _ = volumes_before_calibration.shape
    volumes_for_reference: Vector = volumes_before_calibration[0]

    energies_after_calibration = np.empty(volumes_before_calibration.shape)
    for i in range(configurations_amount):
        strains_before_calibration = calculate_eulerian_strain(
            volumes_before_calibration[i, 0], volumes_before_calibration[i]
        )
        strains_after_calibration = calculate_eulerian_strain(
            volumes_before_calibration[i, 0], volumes_for_reference
        )
        _, energies_after_calibration[i, :] = polynomial_least_square_fitting(
            strains_before_calibration,
            energies_before_calibration[i],
            strains_after_calibration,
            order=order,
        )
    return energies_after_calibration


if __name__ == "__main__":
    import doctest

    doctest.testmod()
