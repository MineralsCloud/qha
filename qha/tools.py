#!/usr/bin/env python3
"""
:mod:`tools` -- Tools used in this package
==========================================

.. module tools
   :platform: Unix, Windows, Mac, Linux
   :synopsis: This module defines some tools used in this package.
.. moduleauthor:: Qi Zhang <qz2280@columbia.edu>
.. moduleauthor:: Tian Qin <qinxx197@umn.edu>
"""

from typing import Callable, Optional

import numpy as np
from numba import jit, guvectorize, float64, int64

from qha.fitting import polynomial_least_square_fitting
from qha.grid_interpolation import calc_eulerian_strain
from qha.type_aliases import Vector, Scalar, Matrix

# ===================== What can be exported? =====================
__all__ = ['find_nearest', 'vectorized_find_nearest', 'lagrange3', 'lagrange4', 'is_monotonic_decreasing',
           'is_monotonic_increasing', 'arange', 'calibrate_energy_on_reference']


@jit(nopython=True)
def _lagrange4(x: float, x0, x1, x2, x3, y0, y1, y2, y3) -> float:
    return (x - x1) * (x - x2) * (x - x3) / (x0 - x1) / (x0 - x2) / (x0 - x3) * y0 + \
           (x - x0) * (x - x2) * (x - x3) / (x1 - x0) / (x1 - x2) / (x1 - x3) * y1 + \
           (x - x0) * (x - x1) * (x - x3) / (x2 - x0) / (x2 - x1) / (x2 - x3) * y2 + \
           (x - x0) * (x - x1) * (x - x2) / (x3 - x0) / (x3 - x1) / (x3 - x2) * y3


def lagrange4(xs: Vector, ys: Vector) -> Callable[[float], float]:
    """
    Fourth-order Lagrange interpolation, referenced from
    `here <http://mathworld.wolfram.com/LagrangeInterpolatingPolynomial.html>`_.

    :param xs:
    :param ys:
    :return:
    """
    if not len(xs) == len(ys) == 4:
        raise ValueError('The *xs* and *ys* must both have length 4!')

    x0, x1, x2, x3 = xs
    y0, y1, y2, y3 = ys

    @jit(nopython=True, nogil=True)
    def f(x: float) -> float:
        """
        A helper which function only does the evaluation.

        :param x: The variable on which the 4th-order Lagrange polynomial is going to be applied.
        :return: The value of the 4th-order Lagrange polynomial :math:`L(x)`.
        """
        return (x - x1) * (x - x2) * (x - x3) / (x0 - x1) / (x0 - x2) / (x0 - x3) * y0 + \
               (x - x0) * (x - x2) * (x - x3) / (x1 - x0) / (x1 - x2) / (x1 - x3) * y1 + \
               (x - x0) * (x - x1) * (x - x3) / (x2 - x0) / (x2 - x1) / (x2 - x3) * y2 + \
               (x - x0) * (x - x1) * (x - x2) / (x3 - x0) / (x3 - x1) / (x3 - x2) * y3

    return f


def lagrange3(xs: Vector, ys: Vector) -> Callable[[float], float]:
    """
    Third-order Lagrange interpolation, referenced from
    `here <http://mathworld.wolfram.com/LagrangeInterpolatingPolynomial.html>`_.

    .. doctest::

        >>> xs = [0, 1, 3]
        >>> ys = [2, 4, 5]
        >>> f = lagrange3(xs, ys)
        >>> f(2.5)
        5.125

    :param xs:
    :param ys:
    :return:
    """
    if not len(xs) == len(ys) == 3:
        raise ValueError('The *xs* and *ys* must both have length 3!')

    if len(set(xs)) < 3:  # The ``set`` will remove duplicated items.
        raise ValueError('Some elements of *xs* are duplicated!')

    x0, x1, x2 = xs
    y0, y1, y2 = ys

    @jit(nopython=True, nogil=True)
    def f(x: float) -> float:
        """
        A helper which function only does the evaluation.

        :param x: The variable on which the 3rd-order Lagrange polynomial is going to be applied.
        :return: The value of the 3rd-order Lagrange polynomial :math:`L(x)`.
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
    If *array* is unsorted, consider first using an :math:`O(n \log n)` sort and then use this function.
    Referenced from `here <https://stackoverflow.com/questions/2566412/find-nearest-value-in-numpy-array>`_.

    :param array: An array of monotonic increasing reals filled.
    :param value: The value which you want to find between two of the consecutive elements in *array*.
    :return: The index, see above.

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

    :param array: An array of monotonic increasing reals filled.
    :param values: An array of values, each of which is one between two of the consecutive elements in *array*.
    :param result: An array of indices.
    :return: The *result* array.
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
    :param step: The difference between any of the two elements.
    :return: An arithmetic progression.
    """
    return np.array([start + step * n for n in range(int(num))])


def is_monotonic_decreasing(array: Vector) -> bool:
    """
    Check whether the *array* is monotonic decreasing or not.
    For example, in QHA calculation, the volumes should be listed as decreasing array,
    and the pressures should be monotonic increasing.
    This function can be used to check whether the volumes are in the right order.

    .. doctest::

        >>> is_monotonic_decreasing([1, 2, 4, 5, 9])
        False
        >>> is_monotonic_decreasing([2, -5, -10, -20])
        True

    :param array: The array to be evaluated.
    :return: ``True`` if *array* is monotonic decreasing, otherwise ``False``.
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
    :return: ``True`` if *array* is monotonic increasing, otherwise ``False``.
    """
    dx = np.diff(array)
    return np.all(dx >= 0)


def calibrate_energy_on_reference(volumes_before_calibration: Matrix, energies_before_calibration: Matrix,
                                  order: Optional[int] = 3):
    """
    In multi-configuration system calculation, volume set of each calculation may varies a little,
    This function would make the volume set  of configuration 1 (normally, the most populated configuration)
    as a reference volume set, then calibrate the energies of all configurations to this reference volume set.

    :param volumes_before_calibration: Original volume sets of all configurations
    :param energies_before_calibration: Free energies of all configurations on the corresponding volume sets.
    :param order: The order of Birch--Murnaghan EOS fitting.
    :return: Free energies of each configuration on referenced volumes (usually the volumes of the first configuration).
    """
    configurations_amount, _ = volumes_before_calibration.shape
    volumes_for_reference: Vector = volumes_before_calibration[0]

    energies_after_calibration = np.empty(volumes_before_calibration.shape)
    for i in range(configurations_amount):
        strains_before_calibration = calc_eulerian_strain(volumes_before_calibration[i, 0],
                                                          volumes_before_calibration[i])
        strains_after_calibration = calc_eulerian_strain(volumes_before_calibration[i, 0], volumes_for_reference)
        _, energies_after_calibration[i, :] = polynomial_least_square_fitting(strains_before_calibration,
                                                                              energies_before_calibration[i],
                                                                              strains_after_calibration,
                                                                              order=order)
    return energies_after_calibration


if __name__ == '__main__':
    import doctest

    doctest.testmod()
