#!/usr/bin/env python3

import argparse
import sys

from qha import __version__
from qha.cli.handler import QHACommandHandler


class QHAArgumentParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.init_parser()
        self.subparsers = self.parser.add_subparsers(
            dest='command'
        )
        self.handlers = []

    def add_handler(self, cmd: str, handler: QHACommandHandler, aliases: list = []):
        subparsers = self.subparsers.add_parser(cmd, aliases=aliases)
        self.handlers.append({
            'command': cmd,
            'handler': handler,
            'parser': subparsers,
            'aliases': aliases
        })
        handler.init_parser(subparsers)

    def parse_args(self, args=None, namespace=None):
        namespace = self.parser.parse_args(args, namespace)
        command = namespace.command
        try:
            program = next(program for program in self.handlers
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
