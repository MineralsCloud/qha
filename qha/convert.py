#!/usr/bin/env python3

import argparse

import qha
from qha.input_maker import FromQEOutput

parser = argparse.ArgumentParser()
parser.add_argument('inp_file_list')
parser.add_argument('inp_static')
parser.add_argument('inp_q_points')
parser.add_argument('-v', '--version', action='version', version="current qha version: {0}".format(qha.__version__))

namespace = parser.parse_args()

inp_file_list = namespace.inp_file_list
inp_static = namespace.inp_static
inp_q_points = namespace.inp_q_points


def main():
    converter = FromQEOutput(inp_file_list, inp_static, inp_q_points)
    converter.read_file_list()
    converter.read_static()
    converter.read_q_points()
    converter.read_frequency_files()
    converter.write_to_file()
