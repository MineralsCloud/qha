#!/usr/bin/env python3
"""
.. module type_aliases
   :platform: Unix, Windows, Mac, Linux
   :synopsis: This module defines several data types that will remind the user what input should be given
    throughout the calculation.
    The ``Scalar`` type is just a number type;
    the ``Vector`` type is a 1D-array type, can be a list, a tuple, or a ``numpy`` array of floating-point numbers;
    the ``Matrix`` type is a 2D-array type, containing two dimensions of floating-point numbers;
    the ``Array3D`` type is a 3D-array type, containing three dimensions of floating-point numbers;
    and the ``Array4D`` type is a 4D-array type, containing four dimensions of floating-point numbers.
    These types will not affect the code, they are defined to tell the users what is inside the developers' minds
    when they are coding.
.. moduleauthor:: Qi Zhang <qz2280@columbia.edu>
"""

from numba import float64

# ===================== What can be exported? =====================
__all__ = ['Scalar', 'Vector', 'Matrix', 'Array3D', 'Array4D']

Scalar = float64  # 0-dimensional float
Vector = float64[:]  # 1-dimensional floats
Matrix = float64[:, :]  # 2-dimensional floats
Array3D = float64[:, :, :]  # 3-dimensional floats
Array4D = float64[:, :, :, :]  # 4-dimensional floats
