#!/usr/bin/env python3

import argparse
import sys
import pkg_resources

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
    
    def add_plugin_programs(self):
        for entry_point in pkg_resources.iter_entry_points(group='qha.applications'):
            klass = entry_point.load()
            if 'command' in dir(klass):
                command = klass.command
            else:
                raise RuntimeError('The plugin program %s does not have a sub-command!' % repr(klass))
            aliases = klass.aliases if 'aliases' in dir(klass) else None
            program = klass()
            self.add_program(command, program, aliases)
    
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
