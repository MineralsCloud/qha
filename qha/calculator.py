#!/usr/bin/env python3
"""
:mod: calculator
================

.. module calculator
   :platform: Unix, Windows, Mac, Linux
   :synopsis: Read file and write calculated value to files
.. moduleauthor:: Tian Qin <qinxx197@umn.edu>
.. moduleauthor:: Qi Zhang <qz2280@columbia.edu>
"""

import textwrap
from typing import Dict, Any, Optional

import numpy as np
import pandas as pd
from lazy_property import LazyProperty

import qha.multi_configurations.different_phonon_dos as different_phonon_dos
import qha.multi_configurations.same_phonon_dos as same_phonon_dos
import qha.tools
from qha.grid_interpolation import RefineGrid
from qha.out import save_to_output
from qha.readers import read_input
from qha.single_configuration import free_energy
from qha.thermodynamics import *
from qha.type_aliases import Vector
from qha.unit_conversion import gpa_to_ry_b3, ry_b3_to_gpa, b3_to_a3, ry_to_j_mol, ry_to_ev
from qha.v2p import v2p


class Calculator:
    def __init__(self, user_settings: Dict[str, Any]):
        runtime_settings = dict()

        allowed_keys = ('same_phonon_dos', 'input', 'volume_energies',
                        'calculate', 'static_only', 'energy_unit',
                        'NT', 'DT', 'DT_SAMPLE',
                        'P_MIN', 'NTV', 'DELTA_P', 'DELTA_P_SAMPLE',
                        'calculate', 'volume_ratio', 'order', 'p_min_modifier',
                        'T4FV', 'output_directory', 'plot_results', 'high_verbosity', 'qha_output')

        for key in allowed_keys:
            try:
                runtime_settings.update({key: user_settings[key]})
            except KeyError:
                continue  # If a key is not set in user settings, use the default.

        self._settings = runtime_settings

        self._formula_unit_number = None
        self._volumes = None
        self._static_energies = None
        self._frequencies = None
        self._q_weights = None

        self._finer_volumes_au = None
        self._f_tv_au = None
        self._v_ratio = None

    @property
    def settings(self) -> Dict[str, Any]:
        """
        This is a read-only property.

        :return: The computational settings given by the user, combined with default settings. The user settings
            will cover the default settings.
        """
        return self._settings

    @property
    def formula_unit_number(self) -> Optional[int]:
        return self._formula_unit_number

    @property
    def volumes(self):
        return self._volumes

    @property
    def static_energies(self):
        return self._static_energies

    @property
    def frequencies(self):
        return self._frequencies

    @property
    def q_weights(self):
        return self._q_weights

    @property
    def finer_volumes_au(self):
        return self._finer_volumes_au

    @property
    def f_tv_au(self):
        return self._f_tv_au

    @property
    def v_ratio(self) -> Optional[float]:
        return self._v_ratio

    def read_input(self):
        try:
            formula_unit_number, volumes, static_energies, frequencies, q_weights = read_input(self.settings['input'])
        except KeyError:
            raise KeyError("The 'input' option must be given in your settings!")

        if not qha.tools.is_monotonic_decreasing(volumes):
            raise RuntimeError("Check the input file to make sure the volume decreases!")

        self._formula_unit_number: int = formula_unit_number
        self._volumes = volumes
        self._static_energies = static_energies
        self._frequencies = frequencies
        self._q_weights = q_weights

    @LazyProperty
    def temperature_array(self) -> Vector:
        """
        The temperature calculated to derive free energy at that temperature.

        :return:
        """
        # Normally, the last 2 temperature points in Cp are not accurate.
        # Here 4 more points are added for calculation, but they will be removed at the output files.
        return qha.tools.arange(0, self.settings['NT'] + 4, self.settings['DT'])

    def refine_grid(self):
        d = self.settings

        try:
            p_min, p_min_modifier, ntv, order = d['P_MIN'], d['p_min_modifier'], d['NTV'], d['order']
        except KeyError:
            raise KeyError("All the 'P_MIN', 'p_min_modifier', 'NTV', 'order' options must be given in your settings!")

        r = RefineGrid(p_min - p_min_modifier, ntv, option=order)

        if 'volume_ratio' in d:
            self._finer_volumes_au, self._f_tv_au, self._v_ratio = r.refine_grids(self.volumes, self.vib_ry,
                                                                                  ratio=d['volume_ratio'])
        else:
            self._finer_volumes_au, self._f_tv_au, self._v_ratio = r.refine_grids(self.volumes, self.vib_ry)

    @LazyProperty
    def vib_ry(self):
        # We grep all the arguments once since they are being invoked for thousands of times, and will be an overhead.
        args = self.q_weights, self.static_energies, self.frequencies, self.settings['static_only']

        mat = np.empty((self.temperature_array.size, self.volumes.size))
        for i, t in enumerate(self.temperature_array):
            mat[i] = free_energy(t, *(arg for arg in args))

        return mat

    @LazyProperty
    def thermodynamic_potentials(self) -> Dict[str, Any]:
        return thermodynamic_potentials(self.temperature_array, self.finer_volumes_au, self.f_tv_au, self.p_tv_au)

    @LazyProperty
    def temperature_sample_array(self):
        return self.temperature_array[0::int(self.settings['DT_SAMPLE'] / self.settings['DT'])]

    @LazyProperty
    def desired_pressures_gpa(self):
        d = self.settings
        return qha.tools.arange(d['P_MIN'], d['NTV'], d['DELTA_P'])

    @LazyProperty
    def desired_pressures(self):
        return gpa_to_ry_b3(self.desired_pressures_gpa)

    @LazyProperty
    def pressure_sample_array(self):
        return self.desired_pressures_gpa[0::int(self.settings['DELTA_P_SAMPLE'] / self.settings['DELTA_P'])]

    @LazyProperty
    def finer_volumes_ang3(self):
        return b3_to_a3(self.finer_volumes_au)

    @LazyProperty
    def vib_ev(self):
        return ry_to_ev(self.vib_ry)

    @LazyProperty
    def volumes_ang3(self):
        return b3_to_a3(self.volumes)

    def desired_pressure_status(self) -> None:
        d = self.settings

        if d['high_verbosity']:
            save_to_output(d['qha_output'], "The pressure range can be dealt with: [{0:6.2f} to {1:6.2f}] GPa".format(
                self.p_tv_gpa[:, 0].max(), self.p_tv_gpa[:, -1].min()))

        if self.p_tv_gpa[:, -1].min() < self.desired_pressures_gpa.max():
            ntv_max = int((self.p_tv_gpa[:, -1].min() - self.desired_pressures_gpa.min()) / d['DELTA_P'])

            save_to_output(d['qha_output'], textwrap.dedent("""\
                           !!!ATTENTION!!!
                           
                           DESIRED PRESSURE is too high (NTV is too large)!
                           QHA results might not be right!
                           Please reduce the NTV accordingly, for example, try to set NTV < %4d.
                           """.format(ntv_max)))

            raise ValueError("DESIRED PRESSURE is too high (NTV is too large), qha results might not be right!")

    @LazyProperty
    def p_tv_au(self):
        return pressure_tv(self.finer_volumes_au, self.f_tv_au)

    @LazyProperty
    def f_tv_ev(self):
        return ry_to_ev(self.f_tv_au)

    @LazyProperty
    def p_tv_gpa(self):
        return ry_b3_to_gpa(self.p_tv_au)

    @LazyProperty
    def f_tp_au(self):
        return v2p(self.f_tv_au, self.p_tv_au, self.desired_pressures)

    @LazyProperty
    def f_tp_ev(self):
        return ry_to_ev(self.f_tp_au)

    @LazyProperty
    def u_tv_au(self):
        return self.thermodynamic_potentials['U']

    @LazyProperty
    def u_tp_au(self):
        return v2p(self.u_tv_au, self.p_tv_au, self.desired_pressures)

    @LazyProperty
    def u_tp_ev(self):
        return ry_to_ev(self.u_tp_au)

    @LazyProperty
    def h_tv_au(self):
        return self.thermodynamic_potentials['H']

    @LazyProperty
    def h_tp_au(self):
        return v2p(self.h_tv_au, self.p_tv_au, self.desired_pressures)

    @LazyProperty
    def h_tp_ev(self):
        return ry_to_ev(self.h_tp_au)

    @LazyProperty
    def g_tv_au(self):
        return self.thermodynamic_potentials['G']

    @LazyProperty
    def g_tp_au(self):
        return v2p(self.g_tv_au, self.p_tv_au, self.desired_pressures)

    @LazyProperty
    def g_tp_ev(self):
        return ry_to_ev(self.g_tp_au)

    @LazyProperty
    def bt_tv_au(self):
        return isothermal_bulk_modulus(self.finer_volumes_au, self.p_tv_au)

    @LazyProperty
    def bt_tp_au(self):
        return v2p(self.bt_tv_au, self.p_tv_au, self.desired_pressures)

    @LazyProperty
    def bt_tp_gpa(self):
        return ry_b3_to_gpa(self.bt_tp_au)

    @LazyProperty
    def btp_tp(self):
        return bulk_modulus_derivative(self.desired_pressures, self.bt_tp_au)

    @LazyProperty
    def v_tp_au(self):
        return volume_tp(self.finer_volumes_au, self.desired_pressures, self.p_tv_au)

    @LazyProperty
    def v_tp_ang3(self):
        return b3_to_a3(self.v_tp_au)

    @LazyProperty
    def alpha_tp(self):
        return thermal_expansion_coefficient(self.temperature_array, self.v_tp_au)

    @LazyProperty
    def cv_tv_au(self):
        return volume_specific_heat_capacity(self.temperature_array, self.u_tv_au)

    @LazyProperty
    def cv_tp_au(self):
        return v2p(self.cv_tv_au, self.p_tv_au, self.desired_pressures)

    @LazyProperty
    def cv_tp_jmol(self):
        return ry_to_j_mol(self.cv_tp_au) / self.formula_unit_number

    @LazyProperty
    def gamma_tp(self):
        return gruneisen_parameter(self.v_tp_au, self.bt_tp_au, self.alpha_tp, self.cv_tp_au)

    @LazyProperty
    def bs_tp_au(self):
        return adiabatic_bulk_modulus(self.bt_tp_au, self.alpha_tp, self.gamma_tp, self.temperature_array)

    @LazyProperty
    def bs_tp_gpa(self):
        return ry_b3_to_gpa(self.bs_tp_au)

    @LazyProperty
    def cp_tp_au(self):
        return pressure_specific_heat_capacity(self.cv_tp_au, self.alpha_tp, self.gamma_tp, self.temperature_array)

    @LazyProperty
    def cp_tp_jmol(self):
        return pressure_specific_heat_capacity(self.cv_tp_jmol, self.alpha_tp, self.gamma_tp, self.temperature_array)


class SamePhDOSCalculator(Calculator):
    def __init__(self, user_settings):
        super().__init__(user_settings)

        self._volume_energy = None
        self._degeneracies = None

    @property
    def volume_energy(self):
        return self._volume_energy

    @property
    def degeneracies(self):
        return self._degeneracies

    def read_energy_degeneracy(self):
        volume_energies = pd.read_csv(self.settings['volume_energies'], sep='\s+', index_col='volume')
        self._degeneracies = tuple(self.settings['input'].values())

        self._volume_energy = volume_energies

    @LazyProperty
    def vib_ry(self):
        v = np.empty(self.temperature_array.shape)

        for i, t in enumerate(self.temperature_array):
            v[i] = same_phonon_dos.FreeEnergy(t, self.volume_energy.as_matrix(), self.degeneracies, self.q_weights,
                                              self.frequencies).total
        return v


class DifferentPhDOSCalculator(Calculator):
    def __init__(self, user_settings: Dict[str, Any]):
        super().__init__(user_settings)

        self._degeneracies = None

    @property
    def degeneracies(self):
        return self._degeneracies

    @property
    def volumes(self):
        # TODO: This is a bad style, they should be consistent
        return self._volumes[0]

    def read_input(self):
        self._degeneracies = tuple(self.settings['input'].values())
        input_data_files = tuple(self.settings['input'].keys())

        formula_unit_numbers = []
        volumes = []
        static_energies = []
        frequencies = []
        q_weights = []

        for inp in input_data_files:
            nm_tmp, volumes_tmp, static_energies_tmp, freq_tmp, weights_tmp = read_input(inp)

            if not qha.tools.is_monotonic_decreasing(volumes_tmp):
                # TODO: Clean this sentence
                save_to_output(self.settings['qha_output'], "Check the input file to make sure the volume decreases")
                raise ValueError("Check the input file to make sure the volumes are monotonic decreasing!")

            formula_unit_numbers.append(nm_tmp)
            volumes.append(volumes_tmp)
            static_energies.append(static_energies_tmp)
            frequencies.append(freq_tmp)
            q_weights.append(weights_tmp)

        formula_unit_numbers = np.array(formula_unit_numbers)
        volumes = np.array(volumes)
        static_energies = np.array(static_energies)
        frequencies = np.array(frequencies)
        q_weights = np.array(q_weights)

        if not len(set(formula_unit_numbers)) == 1:
            raise RuntimeError("All the formula unit number in all inputs should be the same!")

        if len(volumes.shape) == 1:
            raise RuntimeError("All configurations should have same number of volumes!")

        self._formula_unit_number = formula_unit_numbers[0]  # Choose any of them since they are all the same
        self._volumes = volumes
        self._static_energies = static_energies
        self._frequencies = frequencies
        self._q_weights = q_weights

    @LazyProperty
    def vib_ry(self):
        # We grep all the arguments once since they are being invoked for thousands of times, and will be an overhead.
        args = self.static_energies, self.degeneracies, self.q_weights, self.frequencies, self._volumes, \
               self.settings['static_only']

        mat = np.empty((self.temperature_array.size, self._volumes.shape[1]))
        for i, t in enumerate(self.temperature_array):
            mat[i] = different_phonon_dos.PartitionFunction(t, *(arg for arg in args)).derive_free_energy

        return mat
