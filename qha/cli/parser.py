#!/usr/bin/env python3
"""
.. module cli.parser
   :platform: Unix, Windows, Mac, Linux
.. moduleauthor:: Chenxing Luo <chenxing.luo@columbia.edu>
.. moduleauthor:: Qi Zhang <qz2280@columbia.edu>
"""

import argparse

import pkg_resources

from qha import __version__
from qha.cli.handler import QHACommandHandler


class SubCommandResolvers:
    """
    This is just a simple dataclass for storing useful parsers that will be dealing with sub-commands.

    :param handler: The handler that will do the corresponding tasks to the sub-command.
    :param parser: The parser that will parse the (optional) arguments of the sub-command.
    """

    def __init__(self, handler, parser):
        self.handler = handler
        self.parser = parser


class QHAArgumentParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.init_parser()
        self.subparsers = self.parser.add_subparsers(
            dest='command'
        )
        self.handlers = dict()

    def init_parser(self):
        """
        A function that handles a group of (optional) arguments which will shared with all the sub-commands.
        The available arguments are:

        1. short version: ``-V``, long version: ``--version``, the current release version of ``qha``.
        2. short version: ``-h``, long version: ``--help``, the help document of ``qha``.
        """
        self.parser.add_argument(
            '-V', '--version',
            action='version',
            version="current qha version: {0}".format(__version__),
            help='The current release version of ``qha``.'
        )

    def register_handler(self, command: str, handler: QHACommandHandler, *aliases):
        """
        Each handler corresponds to one sub-command. All sub-commands now available are:

        1. ``convert``
        2. ``run``
        3. ``plot``

        They can be added to the parser and will be parsed.

        :param command: The sub-command's name.
        :param handler: The handler that will do corresponding task, each handler is paired with a sub-command.
        :param aliases: The aliases of the sub-command. It can be an iterable. For example, ``convert`` sub-command
            has an alias that is ``cv``.
        """
        if not isinstance(command, str):
            raise TypeError("Argument *command* should be a string!")

        if not isinstance(handler, QHACommandHandler):
            raise TypeError("Argument *handler* should be a ``QHACommandHandler`` instance!")

        new_parser = self.subparsers.add_parser(command, aliases=list(aliases))
        self.handlers.update(
            dict.fromkeys(
                (command, *aliases),
                SubCommandResolvers(
                    handler=handler,
                    parser=new_parser,
                )
            )
        )
        handler.init_parser(new_parser)

    def parse_args(self, args=None, namespace=None):
        """
        Parse the arguments that is given to ``qha`` command.

        :param args: The (optional) arguments given by the user.
        :param namespace: Exactly the same as the same-name argument in ``argparse.ArgumentParser.parse_args``.
            See the official
            `documentation <https://docs.python.org/3.7/library/argparse.html#argparse.ArgumentParser.parse_args>`_
        :return: Based on argument *namespace*, could be an ``argparse.Namespace`` object or the object specified
            by *namespace*.
        """
        return self.parser.parse_args(args, namespace)

    def invoke_handler(self, namespace):
        """
        Invoke the handler based on *namespace* argument.

        :param namespace: The namespace returned by ``parse_args`` method.
        """
        try:
            command: str = getattr(namespace, 'command')
        except AttributeError:
            raise AttributeError("Argument *namespace* does not have an ``command`` attribute!")

        try:
            handler: QHACommandHandler = self.handlers[command].handler
            handler.run(namespace)
        except KeyError:
            raise ValueError("Command '{0}' is not recognized!".format(command))

    def load_plugins(self):
        """
        Load plugins. Leave for the future plugin system.
        """
        for plugin in pkg_resources.iter_entry_points(group='qha.plugins'):
            klass = plugin.load()
            aliases = klass.aliases if 'aliases' in dir(klass) else None
            self.register_handler(plugin.name, klass(), *aliases)
