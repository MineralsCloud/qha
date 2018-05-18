#!/usr/bin/env python3
"""
.. module type_aliases
   :platform: Unix, Windows, Mac, Linux
   :synopsis: This module defines several data type that will be useful in the whole calculation.
    The ``Scalar`` type is just a Numba type;
    the ``Vector`` type is a 1D-array type, can be list, tuple, or ``numpy.ndarray`` of ``float`` numbers;
    the ``Matrix`` type is a 2D-array type, containing 2 dimensions of ``float`` numbers;
    the ``Array3D`` type is a 3D-array type, containing 3 dimensions of ``float`` numbers;
    and the ``Array4D`` type is a 4D-array type, containing 4 dimensions of ``float`` numbers.
    Those types will not have effect on the code, just telling the users what is inside the developers' minds
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
