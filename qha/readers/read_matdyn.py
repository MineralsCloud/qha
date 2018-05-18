#!/usr/bin/env python3
"""
.. module read_matdyn
   :platform: Unix, Windows, Mac, Linux
   :synopsis: doc
.. moduleauthor:: Qi Zhang <qz2280@columbia.edu>
"""

import pathlib
import re
from typing import Optional, Tuple, List, Iterator, Iterable

import numpy as np
import scientific_string
from text_stream import TextStream

# ===================== What can be exported? =====================
__all__ = ['FreqLexer', 'FreqParser', 'auto_parse', 'read_matdyn']


class FreqLexer:
    def __init__(self, inp: Optional[str]):
        self.text_stream = TextStream(inp)
        self.commenters = '!'
        self.nbnd = None
        self.nks = None

    def lex(self) -> Tuple[List[float], ...]:
        generator: Iterator[str] = self.text_stream.generator()
        for line in generator:
            if '&plot' in line:
                match = re.search("nbnd=\s*(\d+).*nks=\s*(\d+)", line, flags=re.IGNORECASE)
                if match is None:
                    raise RuntimeError('Something went wrong!')
                else:
                    try:
                        self.nbnd, self.nks = scientific_string.strings_to_integers(match.groups())
                    except ValueError:
                        raise
                    break
        bands = []
        qs = []
        for line in generator:
            line_stripped = line.strip()
            if not line_stripped or line_stripped.startswith(self.commenters):  # empty line or comment line
                continue
            _: List[float] = scientific_string.strings_to_floats(line_stripped.split())
            if len(_) == self.nbnd:
                bands.append(_)
            elif len(_) == 3:
                qs.append(_)
            else:
                raise ValueError('Unknown value read!')
        return bands, qs


class FreqParser:
    def __init__(self, lexer: FreqLexer):
        if isinstance(lexer, FreqLexer):
            self.lexer = lexer
        else:
            raise TypeError("The argument you gave for *lexer* is not an instance of 'FreqLexer'!")
        self.nbnd = None
        self.nks = None
        self.bands, self.qs = self.setup()

    def setup(self):
        try:
            bands, qs = self.lexer.lex()
        except ValueError:
            raise
        return np.array(bands), np.array(qs)

    def check(self) -> bool:
        if self.bands.shape == (self.lexer.nks, self.lexer.nbnd) and self.qs.shape == (self.lexer.nks, 3):
            self.nbnd = self.lexer.nbnd
            self.nks = self.lexer.nks
            return True
        else:
            if self.bands.shape != (self.lexer.nks, self.lexer.nbnd):
                print('The shape of bands is incorrect!')
            else:
                print('The shape of q-points is incorrect!')
            return False

    def separate_bands(self) -> Optional[List[np.ndarray]]:
        if not self.check():
            return None
        else:
            bands = []
            for i in range(self.nbnd):
                bands.append(self.bands[:, i])
            return bands


def auto_parse(inp: Optional[str]) -> Tuple[Optional[List[np.ndarray]], np.ndarray]:
    parser = FreqParser(FreqLexer(inp))
    return parser.separate_bands(), parser.qs


def read_matdyn(files: Iterable[str]) -> np.ndarray:
    bands = []
    for file in files:
        if not pathlib.Path(file).is_file():
            raise ValueError("{0} is not a file!".format(file))
        f = FreqParser(FreqLexer(file))
        bands.append(f.bands)
    return np.array(bands)
