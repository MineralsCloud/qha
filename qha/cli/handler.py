#!/usr/bin/env python3

import abc
import argparse


class QHACommandHandler(abc.ABC):
    @abc.abstractmethod
    def init_parser(self, parser: argparse.ArgumentParser):
        ...

    @abc.abstractmethod
    def run(self, namespace):
        ...
