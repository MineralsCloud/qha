#!/usr/bin/env python3

import argparse
from collections import namedtuple

import pkg_resources

from qha import __version__
from qha.cli.handler import QHACommandHandler

CommandResolvers = namedtuple('CommandResolvers', ['handler', 'parser'])


class QHAArgumentParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.init_parser()
        self.subparsers = self.parser.add_subparsers(
            dest='command'
        )
        self.handlers = dict()

    def add_handler(self, command: str, handler: QHACommandHandler, *aliases):
        new_parser = self.subparsers.add_parser(command, aliases=list(aliases))
        self.handlers.update(
            dict.fromkeys(
                (command, *aliases),
                CommandResolvers(
                    handler=handler,
                    parser=new_parser,
                )
            )
        )
        handler.init_parser(new_parser)

    def parse_args(self, args=None, namespace=None) -> argparse.Namespace:
        return self.parser.parse_args(args, namespace)

    def invoke_handler(self, namespace):
        command: str = namespace.command
        try:
            handler: QHACommandHandler = self.handlers[command].handler
            handler.run(namespace)
        except KeyError:
            raise ValueError("Command '{0}' is not recognized!".format(command))

    def init_parser(self):
        self.parser.add_argument(
            '-V', '--version',
            action='version',
            version="current qha version: {0}".format(__version__)
        )

    def load_plugins(self):
        for plugin in pkg_resources.iter_entry_points(group='qha.plugins'):
            klass = plugin.load()
            aliases = klass.aliases if 'aliases' in dir(klass) else None
            self.add_handler(plugin.name, klass(), *aliases)
