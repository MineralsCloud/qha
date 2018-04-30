#!/usr/bin/env python3
"""
:mod: read_input
================================

.. module read_input
   :platform: Unix, Windows, Mac, Linux
   :synopsis: Read file and write calculated value to files
.. moduleauthor:: Qi Zhang <qz2280@columbia.edu>
.. moduleauthor:: Tian Qin <qinxx197@umn.edu>
"""

import pathlib
import re
from typing import Iterator

import numpy as np
from scientific_string import strings_to_integers
from text_stream import TextStream

# ===================== What can be exported? =====================
__all__ = ['read_input']


def read_input(inp: str):
    """
    Can be a string directing to a file, or the file's content directly.

    :param inp: The filename or file's path.
    :return:
    """
    text_stream = TextStream(pathlib.Path(inp))
    gen: Iterator[str] = text_stream.generator_telling_position()

    volume_number = None
    q_point_number = None
    mode_number = None
    formula_unit_number = None
    offset = 0

    # Now we start reading some metadata.
    regex0 = re.compile("\s*(\d+)[\s,]*(\d+)[\s,]*(\d+)[\s,]*(\d+)")

    for line, offset in gen:
        if not line.strip() or line.startswith('#'):
            continue
        match = regex0.search(line)
        if match is None:
            continue
        else:
            volume_number, q_point_number, mode_number, formula_unit_number = strings_to_integers(match.groups())
            break

    # If the metadata is not found, check the *inp*!
    if any(_ is None for _ in (volume_number, q_point_number, mode_number)):
        raise ValueError("At least one of the desired values 'nv', 'nq', 'np' is not found in file {0}!".format(inp))

    # Generate containers for storing the following data.
    volumes = np.empty(volume_number, dtype=float)
    static_energies = np.empty(volume_number, dtype=float)
    frequencies = np.empty((volume_number, q_point_number, mode_number), dtype=float)
    q_weights = np.empty(q_point_number, dtype=float)

    # We start a new iterator from where we stopped.
    gen = text_stream.generator_starts_from(offset)

    i = 0  # volume count
    j = 0  # q-point index, note it is not count like `i`!

    # Now we start reading the energies, volumes, and frequencies.
    regex1 = re.compile("P\s*=\s*-?\d*\.?\d*\s*V\s*=(\s*\d*\.?\d*)\s*E\s*=\s*(-?\d*\.?\d*)", re.IGNORECASE)

    for line in gen:
        if not line.strip():
            continue

        if '=' in line:
            match = regex1.search(line)
            if match is None:
                raise ValueError("Search of pattern {0} failed in line '{1}!".format(regex1.pattern, line))
            else:
                volumes[i], static_energies[i] = match.groups()
                i += 1
                j = 0
            continue

        sp = line.split()
        if len(sp) == 3:
            for k in range(mode_number):  # Note `k` is the index of mode, like `j`, not count like `i`.
                line = next(gen)
                frequencies[i - 1, j, k] = line

            j += 1
            continue

        if 'weight' in line.lower():
            break

    # Now we start reading q-point-weights. We start the exact iterator from where we stopped.
    j = 0

    for line in gen:
        if not line.strip():
            continue

        q_weights[j] = line.split()[-1]
        j += 1

    if i != volume_number:
        raise ValueError('There is something wrong when reading!')

    return formula_unit_number, volumes, static_energies, frequencies, q_weights
