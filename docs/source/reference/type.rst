====================
Types and signatures
====================

This package defines several data type that will be useful in the whole calculation.

1. The ``Scalar`` type is just a Numba ``float64`` type.
2. the ``Vector`` type is a 1D ``float64[:]``, can be list, tuple, or ``numpy.ndarray`` of ``float`` numbers.
3. the ``Matrix`` type is a 2D ``float64[:, :]``, containing 3 dimensions of ``float`` numbers.
4. and the ``Mesh`` type is a 3D ``float64[:, :, :]`` type, containing 3 dimensions of ``float`` numbers.

Those types will not have effect on the code, just telling the users what is inside the developers' minds
when they are coding.