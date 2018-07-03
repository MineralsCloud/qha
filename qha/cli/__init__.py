#!/usr/bin/env python3

import argparse

from qha import __version__


def main():
    parser = argparse.ArgumentParser(prog='qha')
    parser.add_argument('-V', '--version', action='version', version="current qha version: {0}".format(__version__))
    subparsers = parser.add_subparsers(dest='command')

    parser_run = subparsers.add_parser('run')
    parser_run.add_argument('settings', type=str)

    parser_plot = subparsers.add_parser('plot')
    parser_plot.add_argument('settings', type=str)
    parser_plot.add_argument('--outdir', type=str, help='output directory')

    parser_convert = subparsers.add_parser('convert', aliases=['conv'])
    parser_convert.add_argument('inp_file_list', type=str)
    parser_convert.add_argument('inp_static', type=str)
    parser_convert.add_argument('inp_q_points', type=str)

    namespace = parser.parse_args()

    args = vars(namespace)
    command = args['command']
    arguments_for_command = {k: v for k, v in args.items() if k != 'command'}

    from .convert import ConvertHandler
    from .plot import PlotHandler
    from .run import RunHandler

    handler = {
        'run': RunHandler,
        'plot': PlotHandler,
        'convert': ConvertHandler,
        'conv': ConvertHandler
    }[command]

    handler(arguments_for_command).run()


if __name__ == '__main__':
    main()
