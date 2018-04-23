#!/usr/bin/env python3

import os
import re

import numpy as np
from scientific_string import strings_to_floats

# ===================== What can be exported? =====================
__all__ = ['Converter', 'read_qefreq']


class Converter:
    def __init__(self, flist: str, fpve: str, fkpts: str):
        self.flist = flist
        self.fpve = fpve
        self.fkpts = fkpts

        self.nm, self.info_sys, self.freqs_file_list = self.read_file_list()

        self.p, self.v, self.e = self.read_pve()
        self.__kpts, self.wt = self.read_kpts()
        self.num_freqs, self.freqs, self.kpts = self.read_freqs()

    def read_file_list(self):
        freqs_file_list = []
        with open(self.flist, 'r') as f:
            _ = f.readline()
            info_sys = f.readline()
            _ = f.readline()
            tmp_line = f.readline()
            _, nm = tmp_line.strip().split('=')
            _ = f.readline()
            for line in f:
                tmp_line = line.strip()
                freqs_file_list.append(tmp_line)

        return nm, info_sys, freqs_file_list

    def read_pve(self):
        pressures = []
        volumes = []
        energies = []
        with open(self.fpve, 'r') as f:
            for line in f:
                match = re.match("p\s*=\s*(-?\d*\.?\d*)\s*v\s*=\s*(-?\d*\.?\d*)\s*e\s*=\s*(-?\d*\.?\d*)", line,
                                 flags=re.IGNORECASE)
                if match is None:
                    continue
                p, v, e = strings_to_floats(match.groups())
                pressures.append(p), volumes.append(v), energies.append(e)
        return np.array(pressures), np.array(volumes), np.array(energies)

    def read_kpts(self):
        kpts = []
        wt = []
        with open(self.fkpts, 'r') as f:
            for line in f:
                if not line.strip():  # Ignore empty line
                    continue
                tmp_line = line.strip().split()
                kpts.append([tmp_line[0], tmp_line[1], tmp_line[2]])
                wt.append(tmp_line[3])
        kpts = np.array(kpts)
        wt = np.array(wt)
        return kpts, wt

    def read_freqs(self):
        freqs = []
        kpts_freqs = []
        num_volume = len(self.freqs_file_list)
        num_kpts = len(self.__kpts)

        for idx_vol in range(num_volume):
            kpts_tmp, num_freqs, kpts, freqs_tmp = read_qefreq(self.freqs_file_list[idx_vol])
            freqs.append(freqs_tmp)
            kpts_freqs.append(kpts_tmp)
        freqs = np.array(freqs)
        kpts_freqs = np.array(kpts_freqs)
        return num_freqs, freqs, kpts_freqs

    def write_to_input(self, outfile='input.txt'):

        try:
            os.remove(outfile)
        except OSError:
            pass

        kpts = self.kpts
        nfreq = self.num_freqs

        write_to_file(outfile, self.info_sys)
        header = ''
        header = add_to_str(header, 'The file contains frequencies and wieght factors at the END')
        header = add_to_str(header, 'Number of volumes (nv), q-vectors (nq), normal mode (np), formula units(nm)')

        info_str = str(len(self.freqs_file_list)) + '\t' + str(len(self.__kpts)) + '\t' + str(nfreq) + '\t' + str(
            self.nm)
        header = add_to_str(header, info_str)

        write_to_file(outfile, header)
        write_to_file(outfile, '\n')

        for idx_vol in range(len(self.freqs_file_list)):
            pve = 'P=\t' + str(self.p[idx_vol]) + '\tV=\t' + str(self.v[idx_vol]) + '\tE=\t' + str(self.e[idx_vol])
            write_to_file(outfile, pve)
            write_to_file(outfile, '\n')
            q_freqs = ''
            for i_nktps in range(len(kpts[0])):
                q_freqs = add_to_str(q_freqs, kpts[idx_vol][i_nktps][0] + '\t' + kpts[idx_vol][i_nktps][1] + '\t' +
                                     kpts[idx_vol][i_nktps][2])
                for i_nfreq in range(int(nfreq)):
                    q_freqs = add_to_str(q_freqs, str(self.freqs[idx_vol, i_nktps, i_nfreq]))
            write_to_file(outfile, q_freqs)
            write_to_file(outfile, '\n')

        q_wt = 'weight\n'
        for i_nktps in range(len(kpts[0])):
            tmp = self.__kpts[i_nktps][0] + '\t' + self.__kpts[i_nktps][1] + '\t' + self.__kpts[i_nktps][2] + '\t' + \
                  self.wt[i_nktps]
            q_wt = add_to_str(q_wt, tmp)
        write_to_file(outfile, q_wt)


def read_qefreq(fn_freq):
    kpts = []
    freqs = []
    with open(fn_freq, 'r') as f:
        _ = f.readline()
        _ = re.findall(r"[\w']+", _)
        nfreq, nkpts = int(_[2]), int(_[4])

        for i_nktps in range(nkpts):
            kpts.append(f.readline().strip().split())
            for i_nfreq in range(int(nfreq / 6)):
                freqs.append(f.readline().strip().split())

    kpts = np.array(kpts)
    freqs = np.array(freqs)
    return kpts, nfreq, kpts, freqs


def write_to_file(filename, text):
    with open(filename, "a") as f:
        f.write(text)  # +'\n'


def add_to_str(str_name, text):
    return str_name + text + '\n'
