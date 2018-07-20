#!/usr/bin/env python3

import argparse
import sys

from qha import __version__
from qha.cli.program import QHAProgram


class QHAArgumentParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.init_parser()
        self.subparsers = self.parser.add_subparsers(
            dest='command'
        )
        self.programs = []

    def add_program(self, cmd: str, prog: QHAProgram, aliases: list = []):
        subparser = self.subparsers.add_parser(cmd, aliases=aliases)
        self.programs.append({
            'command': cmd,
            'program': prog,
            'parser': subparser,
            'aliases': aliases
        })
        prog.init_parser(subparser)

    def parse_args(self, args=None, namespace=None):
        namespace = self.parser.parse_args(args, namespace)
        command = namespace.command
        try:
            program = next(program for program in self.programs
                           if command == program['command']
                           or command in program['aliases'])['program']
            program.run(namespace)
        except StopIteration:
            self.parser.print_usage(sys.stderr)
        return namespace

    def init_parser(self):
        self.parser.add_argument(
            '-v', '--version', action='version',
            version="current qha version: {0}".format(__version__))
