#!/usr/bin/env python3

import argparse

from qha.readers.matdyn2input import Converter

parser = argparse.ArgumentParser()
parser.add_argument('filename')
parser.add_argument('pve')
parser.add_argument('kpt')

namespace = parser.parse_args()

fn_flist = namespace.filename
fn_pve = namespace.pve  # 'PVE'
fn_kwt = namespace.kpt  # 'q_weights.dat'


def main():
    Converter(fn_flist, fn_pve, fn_kwt).write_to_input()
