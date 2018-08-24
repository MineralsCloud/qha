#!/usr/bin/env python3
"""
.. module cli.handler
   :platform: Unix, Windows, Mac, Linux
.. moduleauthor:: Chenxing Luo <chenxing.luo@columbia.edu>
.. moduleauthor:: Qi Zhang <qz2280@columbia.edu>
"""

import abc
import argparse


class QHACommandHandler(abc.ABC):
    @abc.abstractmethod
    def init_parser(self, parser: argparse.ArgumentParser):
        ...

    @abc.abstractmethod
    def run(self, namespace):
        ...
