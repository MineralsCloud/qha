#!/usr/bin/env python3

from .converter import QHAConverter
from .parser import QHAArgumentParser
from .plotter import QHAPlotter
from .runner import QHARunner


def main():
    parser = QHAArgumentParser()

    qha_converter = QHAConverter()
    parser.add_handler('convert', qha_converter, 'conv')

    qha_runner = QHARunner()
    parser.add_handler('run', qha_runner)

    qha_runner = QHAPlotter()
    parser.add_handler('plot', qha_runner)

    qha_plotter = QHAPlotter()
    parser.add_handler('plot', qha_plotter)

    parser.add_plugin_programs()

    namespace = parser.parse_args()
    parser.invoke_handler(namespace)


if __name__ == '__main__':
    main()
