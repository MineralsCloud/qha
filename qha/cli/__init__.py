#!/usr/bin/env python3

from .converter import QHAConverter
from .parser import QHAArgumentParser
from .plotter import QHAPlotter
from .runner import QHARunner


def main():
    parser = QHAArgumentParser()

    qha_converter = QHAConverter()
    parser.add_program('convert', qha_converter)

    qha_runner = QHARunner()
    parser.add_program('run', qha_runner)

    qha_runner = QHAPlotter()
    parser.add_program('plot', qha_runner)

    namespace = parser.parse_args()


if __name__ == '__main__':
    main()
