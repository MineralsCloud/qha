#!/usr/bin/env python3
"""
.. module cli
   :platform: Unix, Windows, Mac, Linux
.. moduleauthor:: Chenxing Luo <chenxing.luo@columbia.edu>
.. moduleauthor:: Tian Qin <qinxx197@umn.edu>
"""

from .converter import QHAConverter
from .parser import QHAArgumentParser
from .plotter import QHAPlotter
from .runner import QHARunner


def main():
    parser = QHAArgumentParser()

    qha_converter = QHAConverter()
    parser.register_handler('convert', qha_converter, 'conv')

    qha_runner = QHARunner()
    parser.register_handler('run', qha_runner)

    qha_plotter = QHAPlotter()
    parser.register_handler('plot', qha_plotter)

    parser.load_plugins()

    namespace = parser.parse_args()
    parser.invoke_handler(namespace)


if __name__ == '__main__':
    main()
