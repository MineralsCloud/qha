#!/usr/bin/env python3

import pathlib
import tempfile
import unittest

import numpy as np

from qha.basic_io.input_maker import FromQEOutput


class TestFromQEOutput(unittest.TestCase):
    def test_read_frequency_file_splits_adjacent_negative_frequencies(self):
        content = """\
&plot nbnd=   6, nks=   1 /
            0.300000  0.291188  0.276701
-2471.6424-2400.9590-1460.5687-1267.3818  157.7216  181.1466
"""

        with tempfile.TemporaryDirectory() as tmpdir:
            path = pathlib.Path(tmpdir) / "matdyn.freq"
            path.write_text(content)

            q_coordinates, frequencies = FromQEOutput.read_frequency_file(str(path))

        np.testing.assert_array_equal(q_coordinates, [[0.3, 0.291188, 0.276701]])
        np.testing.assert_array_equal(
            frequencies,
            [[-2471.6424, -2400.959, -1460.5687, -1267.3818, 157.7216, 181.1466]],
        )

    def test_read_frequency_file_preserves_exponent_signs(self):
        content = """\
&plot nbnd=   6, nks=   1 /
            0.300000  0.291188  0.276701
 1.0000E-03-2.5000E+02  .3000  4.  +5.0000 -6
"""

        with tempfile.TemporaryDirectory() as tmpdir:
            path = pathlib.Path(tmpdir) / "matdyn.freq"
            path.write_text(content)

            _, frequencies = FromQEOutput.read_frequency_file(str(path))

        np.testing.assert_array_equal(
            frequencies, [[0.001, -250, 0.3, 4, 5, -6]]
        )


if __name__ == "__main__":
    unittest.main()
