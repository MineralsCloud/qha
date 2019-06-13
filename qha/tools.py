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
from numba import float64, guvectorize, int64, jit, vectorize

from qha.fitting import polynomial_least_square_fitting
from qha.grid_interpolation import calculate_eulerian_strain
from qha.type_aliases import Matrix, Scalar, Vector

# ===================== What can be exported? =====================
__all__ = ['find_nearest', 'vectorized_find_nearest', 'lagrange3', 'lagrange4', 'is_monotonic_decreasing',
           'is_monotonic_increasing', 'arange', 'calibrate_energy_on_reference']


def lagrange4(xs: Vector, ys: Vector) -> Callable[[float], float]:
    """
    A third-order Lagrange polynomial function. Given 4 points for interpolation:
    :math:`(x_0, y_0), \\ldots, (x_3, y_3)`, evaluate the Lagrange polynomial on :math:`x`, referenced from
    `Wolfram MathWorld <http://mathworld.wolfram.com/LagrangeInterpolatingPolynomial.html>`_.

    :param xs: A vector of the x-coordinates' of the 4 points.
    :param ys: A vector of the y-coordinates' of the 4 points.
    :return: A function that can evaluate the value of an x-coordinate within the range of
        :math:`[\\text{min}(xs), \\text{max}(xs)]`, where :math:`xs` denotes the argument *xs*.
    """
    if not len(xs) == len(ys) == 4:
        raise ValueError('The *xs* and *ys* must both have length 4!')

    x0, x1, x2, x3 = xs
    y0, y1, y2, y3 = ys

    @vectorize(["float64(float64)"], target='parallel')
    def f(x: float) -> float:
        """
        A helper function that only does the evaluation.

        :param x: The variable on which the Lagrange polynomial is going to be applied.
        :return: The value of the Lagrange polynomial on :math:`x`, i.e., :math:`L(x)`.
        """
        return (x - x1) * (x - x2) * (x - x3) / (x0 - x1) / (x0 - x2) / (x0 - x3) * y0 + \
               (x - x0) * (x - x2) * (x - x3) / (x1 - x0) / (x1 - x2) / (x1 - x3) * y1 + \
               (x - x0) * (x - x1) * (x - x3) / (x2 - x0) / (x2 - x1) / (x2 - x3) * y2 + \
               (x - x0) * (x - x1) * (x - x2) / (x3 - x0) / (x3 - x1) / (x3 - x2) * y3

    return f


def lagrange3(xs: Vector, ys: Vector) -> Callable[[float], float]:
    """
    A second-order Lagrange polynomial function. Given 3 points for interpolation:
    :math:`(x_0, y_0), \\ldots, (x_2, y_2)`, evaluate the Lagrange polynomial on :math:`x`, referenced from
    `Wolfram MathWorld also <http://mathworld.wolfram.com/LagrangeInterpolatingPolynomial.html>`_.

    .. doctest::

        >>> xs = [0, 1, 3]
        >>> ys = [2, 4, 5]
        >>> f = lagrange3(xs, ys)
        >>> f(2.5)
        5.125

    :param xs: A vector of the x-coordinates' of the 3 points.
    :param ys: A vector of the y-coordinates' of the 3 points.
    :return: A function that can evaluate the value of an x-coordinate within the range of
        :math:`[\\text{min}(xs), \\text{max}(xs)]`, where :math:`xs` denotes the argument *xs*.
    """
    if not len(xs) == len(ys) == 3:
        raise ValueError('The *xs* and *ys* must both have length 3!')

    if len(set(xs)) < 3:  # The ``set`` will remove duplicated items.
        raise ValueError('Some elements of *xs* are duplicated!')

    x0, x1, x2 = xs
    y0, y1, y2 = ys

    @vectorize(["float64(float64)"], target='parallel')
    def f(x: float) -> float:
        """
        A helper function that only does the evaluation.

        :param x: The variable on which the Lagrange polynomial is going to be applied.
        :return: The value of the Lagrange polynomial on :math:`x`, i.e., :math:`L(x)`.
        """
        return (x - x1) * (x - x2) / (x0 - x1) / (x0 - x2) * y0 + \
               (x - x0) * (x - x2) / (x1 - x0) / (x1 - x2) * y1 + \
               (x - x0) * (x - x1) / (x2 - x0) / (x2 - x1) * y2

    return f


@jit(nopython=True, nogil=True, cache=True)
def find_nearest(array: Vector, value: Scalar) -> int:
    """
    Given an *array* , and given a *value* , returns an index ``j`` such that *value* is between ``array[j]``
    and ``array[j+1]``. The *array* must be monotonic increasing. ``j=-1`` or ``j=len(array)`` is returned
    to indicate that *value* is out of range below and above respectively.
    If *array* is unsorted, consider first using an :math:`O(n \\log n)` sort and then use this function.
    Referenced from `Stack Overflow <https://stackoverflow.com/questions/2566412/find-nearest-value-in-numpy-array>`_.

    :param array: An array of monotonic increasing real numbers.
    :param value: The value which user wants to find between two of the consecutive elements in *array*.
    :return: The index mentioned above.

    .. doctest::

        >>> find_nearest([1, 3, 4, 6, 9, 11], 3.5)
        1
        >>> find_nearest([1, 3, 4, 6, 9, 11], 0)
        0
        >>> find_nearest([1, 3, 4, 6, 9, 11], 12)
        4
    """
    n: int = len(array)

    if value <= array[0]:
        return 0
    elif value >= array[-1]:
        return n - 2

    j_low = 0  # Initialize lower limit.
    j_up = n - 1  # Initialize upper limit.

    while j_up - j_low > 1:  # If we are not yet done,
        j_mid: int = (j_up + j_low) // 2  # compute a midpoint,
        if value >= array[j_mid]:
            j_low = j_mid  # and replace either the lower limit
        else:
            j_up = j_mid  # or the upper limit, as appropriate.
        # Repeat until the test condition is satisfied.

    return j_low


@guvectorize([(float64[:], float64[:], int64[:])], '(m),(n)->(n)')
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
        raise ValueError('The *values* and *result* arguments should have same length!')

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


def is_monotonic_increasing(array: Vector) -> bool:
    """
    Check whether the *array* is monotonic increasing or not.
    For example, in QHA calculation, the volumes should be listed as decreasing array,
    and the pressures should be monotonic increasing.
    This function can be used to check whether the pressures are in the right order.

    .. doctest::

        >>> is_monotonic_increasing([1, 2, 4, 5, 9])
        True
        >>> is_monotonic_increasing([2, -5, -10, -20])
        False

    :param array: The array to be evaluated.
    :return: ``True`` if the argument *array* is monotonic increasing, otherwise ``False``.
    """
    dx = np.diff(array)
    return np.all(dx >= 0)


def calibrate_energy_on_reference(volumes_before_calibration: Matrix, energies_before_calibration: Matrix,
                                  order: Optional[int] = 3):
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
        strains_before_calibration = calculate_eulerian_strain(volumes_before_calibration[i, 0],
                                                               volumes_before_calibration[i])
        strains_after_calibration = calculate_eulerian_strain(volumes_before_calibration[i, 0], volumes_for_reference)
        _, energies_after_calibration[i, :] = polynomial_least_square_fitting(strains_before_calibration,
                                                                              energies_before_calibration[i],
                                                                              strains_after_calibration,
                                                                              order=order)
    return energies_after_calibration


if __name__ == '__main__':
    import doctest

    doctest.testmod()
