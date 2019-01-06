#!/usr/bin/env python3
"""
.. module make_input
   :platform: Unix, Windows, Mac, Linux
   :synopsis: Use data files from Quantum ESPRESSO and other software to generate a standard input.
.. moduleauthor:: Qi Zhang <qz2280@columbia.edu>
.. moduleauthor:: Tian Qin <qinxx197@umn.edu>
"""

import pathlib
import re
import warnings
from typing import Iterator, List, Tuple, Optional

import numpy as np
import yaml
from scientific_string import strings_to_integers
from text_stream import TextStream

from qha.type_aliases import Vector, Matrix

# ===================== What can be exported? =====================
__all__ = ['FromQEOutput']


class FromQEOutput:
    """
    A class that can generate a standard "input" file for the ``qha run`` command if the original data is given by
    Quantum ESPRESSO.

    :param inp_file_list: A YAML file that contains three keys and values:

        1. ``formula_unit_number``: The number of formula units in a unit cell.
        2. ``comment``: Comment that could be added as the first line of the ``input``,
           which usually specifies the system which user wants to calculate.
        3. ``frequency_files``: A YAML list of strings specifying all the frequency files given by Quantum ESPRESSO
           ``matdyn.x``.

        To become more familiar with YAML syntax, which is used in the "settings" file, please refer to
        `this documentation <http://docs.ansible.com/ansible/latest/reference_appendices/YAMLSyntax.html>`_.
    :param inp_static: A pure text file specifying the energies and pressures of each volume from the
        static calculation. The order of these volumes must be the same as the ``frequency_files`` listing order.
    :param inp_q_points: A pure text file specifying the q-points' coordinates and their corresponding weights in the
        Brillouin zone.
    """

    def __init__(self, inp_file_list: str, inp_static: str, inp_q_points: str):
        self._inp_file_list = inp_file_list
        self._inp_static = inp_static
        self._inp_q_points = inp_q_points
        self._frequency_files: Optional[List[str]] = None

        self.formula_unit_number: Optional[int] = None
        self.comment: Optional[str] = None
        self.pressures = None
        self.volumes = None
        self.static_energies = None
        self.q_coordinates = None
        self.q_weights = None
        self.frequencies = None

    def read_file_list(self) -> None:
        """
        Read all the files' names for frequency files given by Quantum ESPRESSO program ``matdyn.x``.
        """
        with open(self._inp_file_list, 'r') as f:
            d = yaml.load(f)

        self.formula_unit_number = int(d['formula_unit_number'])
        self.comment: str = d['comment']
        self._frequency_files: List[str] = d['frequency_files']

    def read_static(self) -> None:
        """
        Read static information, including pressures (which will not be used in calculation by now),
        optimized volumes, and static energies.
        """
        pressures = []
        volumes = []
        energies = []

        with open(self._inp_static, 'r') as f:
            print(
                "Reading static data: emtpy lines or lines starting with '#' will be ignored!")

            for line in f:
                if not line.strip() or line.startswith('#'):  # Ignore empty line or comment line
                    continue

                match = re.match(r"p\s*=\s*(-?\d*\.?\d*)\s*v\s*=\s*(-?\d*\.?\d*)\s*e\s*=\s*(-?\d*\.?\d*)", line,
                                 flags=re.IGNORECASE)
                if match is None:
                    continue

                p, v, e = match.groups()
                pressures.append(p), volumes.append(v), energies.append(e)

        self.pressures = np.array(pressures, dtype=float)
        self.volumes = np.array(volumes, dtype=float)
        self.static_energies = np.array(energies, dtype=float)

    def read_q_points(self) -> None:
        """
        Read q-points' coordinates and their weights in the Brillouin zone. The q-points' coordinates are supposed to be
        three-dimensional. No other information should be given. If user still wants to,
        write lines that start with ``#``, and then they will be ignored when reading.
        """
        q_coordinates = []
        q_weights = []

        with open(self._inp_q_points, 'r') as f:
            print(
                "Reading q-points file: emtpy lines or lines starting with '#' will be ignored!")

            regex = re.compile(
                r"\s*(-?\d*\.?\d*)\s*(-?\d*\.?\d*)\s*(-?\d*\.?\d*)\s*(-?\d*\.?\d*)")

            for line in f:
                if not line.strip() or line.startswith('#'):  # Ignore empty line or comment line
                    continue

                match = regex.match(line)
                if not regex.match(line):
                    raise RuntimeError(
                        "Unknown line! Should be 3 coordinates and 1 weight, other lines should be commented with '#'.")
                else:
                    g = match.groups()
                    q_coordinates.append(g[0:3])
                    # TODO: Check possible bug, what if the regex match fails
                    q_weights.append(g[3])

        self.q_coordinates = np.array(q_coordinates,
                                      dtype=float)  # TODO: Possible bug, ``np.array([])`` is regarded as ``False``
        self.q_weights = np.array(q_weights, dtype=float)

    @staticmethod
    def read_frequency_file(inp: str) -> Tuple[Vector, Matrix]:
        """
        Read Quantum ESPRESSO's output for phonon frequencies. This method is provided for reading only
        one file.

        :param inp: The name or path of the file.
        :return: The q-space coordinates of each q-point in the file and corresponding frequencies for each
            q-point on each band.
        """
        text_stream = TextStream(pathlib.Path(inp))

        gen: Iterator[str] = text_stream.generator_telling_position()

        q_coordinates = []
        frequencies = []

        regex = re.compile(r"nbnd\s*=\s*(\d*),\s*nks=\s*(\d*)")

        offset = None  # Initialization
        bands_amount = None
        q_points_amount = None

        for line, offset in gen:
            if not line.strip():
                continue

            if 'nbnd' or 'nks' in line:
                match = regex.search(line)

                if not match:
                    raise RuntimeError(
                        "The head line '{0}' is not complete! Here 'nbnd' and 'nks' are not found!".format(line))
                else:
                    bands_amount, q_points_amount = strings_to_integers(
                        match.groups())
                    break

        gen: Iterator[str] = text_stream.generator_starts_from(offset)

        quotient = bands_amount // 6  # QE splits branches into 6 columns per line

        for line in gen:
            if not line.strip():
                continue

            q_coordinates.append(line.split())

            x = np.array([])
            for _ in range(quotient):
                line = next(gen)  # Start a new line
                x = np.hstack((x, line.split()))

            frequencies.append(x)

        q_coordinates = np.array(q_coordinates, dtype=float)
        frequencies = np.array(frequencies, dtype=float)

        if q_coordinates.shape[0] != q_points_amount:
            raise RuntimeError(
                "The number of q-points detected, {0}, is not the same as what specified in head line!".format(
                    q_coordinates.shape[0]))

        if frequencies.shape != (q_points_amount, bands_amount):
            raise RuntimeError(
                "The frequencies array shape '{0}' is not the same as '{1}'!".format(
                    frequencies.shape, (q_points_amount, bands_amount)))

        return q_coordinates, frequencies

    def read_frequency_files(self) -> None:
        """
        Read the phonon frequencies for all files (which are specified in the
        ``frequency_files`` key of the settings file).
        """
        frequencies_for_all_files = []

        if any(_ is None for _ in (self.q_coordinates, self.q_weights)):  # If any of them is ``None``
            self.read_q_points()  # Fill these 2 properties

        for i in range(len(self._frequency_files)):
            q_coordinates, frequencies = self.read_frequency_file(
                self._frequency_files[i])

            # Here I use `allclose` rather than `array_equal` since they may have very little
            # differences even they are supposed to be the same, because of the digits QE gave.
            if not np.allclose(q_coordinates, self.q_coordinates):
                warnings.warn("The q-points' coordinates are different from what specified in the q-point file!",
                              stacklevel=1)

            frequencies_for_all_files.append(frequencies)

        # Shape: (# volumes, # q-points, # bands on each point)
        self.frequencies = np.array(frequencies_for_all_files)

    def write_to_file(self, outfile='input') -> None:
        """
        Write all data to a file *outfile*, which will be regarded as standard input file for ``qha``.

        :param outfile: The path or name of the output file, by default is ``'input'`` (for further calculation).
        """
        path = pathlib.Path(outfile)
        if path.is_file():
            print(
                "Old '{0}' file found, I will backup it before continue.".format(outfile))
            path.rename(outfile + '.backup')

        with open(outfile, 'w') as f:
            f.write("# {0}\n".format(self.comment))
            f.write('# The file contains frequencies and weights at the END!\n')
            f.write(
                '# Number of volumes (nv), q-vectors (nq), normal mode (np), formula units(nm)\n')
            # TODO: Possible bug introduced in formatting
            f.write("{0} {1} {2} {3}\n\n".format(len(self.volumes), len(self.q_weights),
                                                 self.frequencies.shape[-1], self.formula_unit_number))

            for i in range(len(self.volumes)):
                f.write("P={0:20.10f} V={1:20.10f} E={2:20.10f}\n".format(self.pressures[i], self.volumes[i],
                                                                          self.static_energies[i]))

                for j in range(len(self.q_weights)):
                    f.write("{0:12.8f} {1:12.8f} {2:12.8f}\n".format(
                        *self.q_coordinates[j]))

                    for k in range(self.frequencies.shape[-1]):
                        f.write("{0:20.10f}\n".format(
                            self.frequencies[i, j, k]))

            f.write('\nweight\n')
            for j in range(len(self.q_weights)):
                f.write("{0:12.8f} {1:12.8f} {2:12.8f} {3:12.8f}\n".format(
                    *self.q_coordinates[j], self.q_weights[j]))
