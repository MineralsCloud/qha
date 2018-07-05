import argparse
import qha
from qha.cli.program import QHAProgram
import sys

class QHAArgumentParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.init_parser()
        self.subparsers = self.parser.add_subparsers(
            dest='command'
        )
        self.programs = []

    def add_program(self, cmd: str, prog: QHAProgram):
        subparser = self.subparsers.add_parser(cmd)
        self.programs.append({
            'command': cmd,
            'program': prog,
            'parser': subparser
        })
        prog.init_parser(subparser)
    
    def parse_args(self, args=None, namespace=None):
        namespace = self.parser.parse_args(args, namespace)
        try:
            program = next(prog for prog in self.programs
                        if prog['command'] == namespace.command)['program']
            program.run(namespace)
        except StopIteration:
            self.parser.print_usage(sys.stderr)

        return namespace
    
    def init_parser(self):
        self.parser.add_argument(
            '-v', '--version', action='version',
           version="current qha version: {0}".format(qha.__version__))
