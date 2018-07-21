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
        return self.parser.parse_args(args, namespace)

    def invoke_handler(self, namespace):
        command = namespace.command

        try:
            handler = self.handlers[command](namespace)
            handler.run()
        except KeyError:
            raise ValueError("Command is not recognized!")

    def init_parser(self):
        self.parser.add_argument(
            '-v', '--version', action='version',
            version="current qha version: {0}".format(__version__))
