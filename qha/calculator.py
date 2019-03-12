#!/usr/bin/env python3
"""
.. module calculator
   :platform: Unix, Windows, Mac, Linux
   :synopsis: This is one of the most important modules in this package. It defines 3 classes, ``Calculator``,
    ``SamePhDOSCalculator``, and ``DifferentPhDOSCalculator``. The first one can be used to do single configuration
    calculation, the others are for multiple configurations calculation. Among them, the second one is for
    assuming all the configurations have the same phonon density of states, and the third one is for assuming
    all the configurations have different phonon density of states.
.. moduleauthor:: Tian Qin <qinxx197@umn.edu>
.. moduleauthor:: Qi Zhang <qz2280@columbia.edu>
"""

import textwrap
from typing import Dict, Any, Optional

import numpy as np
from lazy_property import LazyProperty

import qha.multi_configurations.different_phonon_dos as different_phonon_dos
import qha.multi_configurations.same_phonon_dos as same_phonon_dos
import qha.tools
from qha.grid_interpolation import FinerGrid
from qha.basic_io.out import save_to_output
from qha.basic_io import read_input
from qha.single_configuration import free_energy
from qha.thermodynamics import *
from qha.type_aliases import Vector
from qha.unit_conversion import gpa_to_ry_b3, ry_b3_to_gpa, b3_to_a3, ry_to_j_mol, ry_to_ev, ry_to_j
from qha.v2p import v2p

# ===================== What can be exported? =====================
__all__ = ['Calculator', 'SamePhDOSCalculator', 'DifferentPhDOSCalculator']


class Calculator:
    def __init__(self, user_settings: Dict[str, Any]):
        runtime_settings = dict()

        allowed_keys = ('input', 'calculation',
                        'thermodynamic_properties', 'static_only', 'energy_unit',
                        'T_MIN', 'NT', 'DT', 'DT_SAMPLE',
                        'P_MIN', 'NTV', 'DELTA_P', 'DELTA_P_SAMPLE',
                        'volume_ratio', 'order', 'p_min_modifier',
                        'T4FV', 'output_directory', 'high_verbosity', 'qha_output')

        for key in allowed_keys:
            try:
                runtime_settings.update({key: user_settings[key]})
            except KeyError:
                # If a key is not set in user settings, use the default.
                continue

        self._settings = runtime_settings

        self._formula_unit_number = None
        self._volumes = None
        self._static_energies = None
        self._frequencies = None
        self._q_weights = None

        self._finer_volumes_bohr3 = None
        self._f_tv_ry = None
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
    def finer_volumes_bohr3(self):
        return self._finer_volumes_bohr3

    @property
    def f_tv_ry(self):
        return self._f_tv_ry

    @property
    def v_ratio(self) -> Optional[float]:
        return self._v_ratio

    def read_input(self):
        try:
            formula_unit_number, volumes, static_energies, frequencies, q_weights = read_input(
                self.settings['input'])
        except KeyError:
            raise KeyError(
                "The 'input' option must be given in your settings!")

        if not qha.tools.is_monotonic_decreasing(volumes):
            raise RuntimeError(
                "Check the input file to make sure the volume decreases!")

        self._formula_unit_number: int = formula_unit_number
        self._volumes = volumes
        self._static_energies = static_energies
        self._frequencies = frequencies
        self._q_weights = q_weights

    @LazyProperty
    def where_negative_frequencies(self) -> Optional[Vector]:
        """
        The indices of negative frequencies are indicated.

        :return:
        """
        if self._frequencies is None:
            # ``None`` is returned
            print("Please invoke ``read_input`` method first!")
        else:
            _ = np.transpose(np.where(self._frequencies < 0))
            if _.size == 0:
                return None

            return _

    @LazyProperty
    def temperature_array(self) -> Vector:
        """
        The temperature calculated to derive free energy at that temperature.

        :return:
        """
        # Normally, the last 2 temperature points in Cp are not accurate.
        # Here 4 more points are added for calculation, but they will be removed at the output files.
        minimum_temperature = self.settings['T_MIN']
        if minimum_temperature < 0:
            raise ValueError("Minimum temperature should be no less than 0!")

        return qha.tools.arange(minimum_temperature, self.settings['NT'] + 4, self.settings['DT'])

    def refine_grid(self):
        d = self.settings

        try:
            p_min, p_min_modifier, ntv, order = d['P_MIN'], d['p_min_modifier'], d['NTV'], d['order']
        except KeyError:
            raise KeyError(
                "All the 'P_MIN', 'p_min_modifier', 'NTV', 'order' options must be given in your settings!")

        r = FinerGrid(p_min - p_min_modifier, ntv, order=order)

        if 'volume_ratio' in d:
            self._finer_volumes_bohr3, self._f_tv_ry, self._v_ratio = r.refine_grid(self.volumes, self.vib_ry,
                                                                                    ratio=d['volume_ratio'])
        else:
            self._finer_volumes_bohr3, self._f_tv_ry, self._v_ratio = r.refine_grid(
                self.volumes, self.vib_ry)

    @LazyProperty
    def vib_ry(self):
        # We grep all the arguments once since they are being invoked for thousands of times, and will be an overhead.
        args = self.q_weights, self.static_energies, self.frequencies, self.settings[
            'static_only']

        mat = np.empty((self.temperature_array.size, self.volumes.size))
        for i, t in enumerate(self.temperature_array):
            mat[i] = free_energy(t, *(arg for arg in args))

        return mat

    @LazyProperty
    def thermodynamic_potentials(self) -> Dict[str, Any]:
        return thermodynamic_potentials(self.temperature_array, self.finer_volumes_bohr3, self.f_tv_ry, self.p_tv_au)

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
        return b3_to_a3(self.finer_volumes_bohr3)

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
            ntv_max = int(
                (self.p_tv_gpa[:, -1].min() - self.desired_pressures_gpa.min()) / d['DELTA_P'])

            save_to_output(d['qha_output'], textwrap.dedent("""\
                           !!!ATTENTION!!!

                           DESIRED PRESSURE is too high (NTV is too large)!
                           QHA results might not be right!
                           Please reduce the NTV accordingly, for example, try to set NTV < {:4d}.
                           """.format(ntv_max)))

            raise ValueError(
                "DESIRED PRESSURE is too high (NTV is too large), qha results might not be right!")

    @LazyProperty
    def p_tv_au(self):
        return pressure(self.finer_volumes_bohr3, self.f_tv_ry)

    @LazyProperty
    def s_tv_j(self):
        return ry_to_j(entropy(self.temperature_array, self.f_tv_ry))

    @LazyProperty
    def f_tv_ev(self):
        return ry_to_ev(self.f_tv_ry)

    @LazyProperty
    def p_tv_gpa(self):
        return ry_b3_to_gpa(self.p_tv_au)

    @LazyProperty
    def f_tp_ry(self):
        return v2p(self.f_tv_ry, self.p_tv_au, self.desired_pressures)

    @LazyProperty
    def f_tp_ev(self):
        return ry_to_ev(self.f_tp_ry)

    @LazyProperty
    def u_tv_ry(self):
        return self.thermodynamic_potentials['U']

    @LazyProperty
    def u_tp_ry(self):
        return v2p(self.u_tv_ry, self.p_tv_au, self.desired_pressures)

    @LazyProperty
    def u_tp_ev(self):
        return ry_to_ev(self.u_tp_ry)

    @LazyProperty
    def h_tv_ry(self):
        return self.thermodynamic_potentials['H']

    @LazyProperty
    def h_tp_ry(self):
        return v2p(self.h_tv_ry, self.p_tv_au, self.desired_pressures)

    @LazyProperty
    def h_tp_ev(self):
        return ry_to_ev(self.h_tp_ry)

    @LazyProperty
    def g_tv_ry(self):
        return self.thermodynamic_potentials['G']

    @LazyProperty
    def g_tp_ry(self):
        return v2p(self.g_tv_ry, self.p_tv_au, self.desired_pressures)

    @LazyProperty
    def g_tp_ev(self):
        return ry_to_ev(self.g_tp_ry)

    @LazyProperty
    def bt_tv_au(self):
        return isothermal_bulk_modulus(self.finer_volumes_bohr3, self.p_tv_au)

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
    def v_tp_bohr3(self):
        return volume(self.finer_volumes_bohr3, self.desired_pressures, self.p_tv_au)

    @LazyProperty
    def v_tp_ang3(self):
        return b3_to_a3(self.v_tp_bohr3)

    @LazyProperty
    def alpha_tp(self):
        return thermal_expansion_coefficient(self.temperature_array, self.v_tp_bohr3)

    @LazyProperty
    def cv_tv_au(self):
        return volumetric_heat_capacity(self.temperature_array, self.u_tv_ry)

    @LazyProperty
    def cv_tp_au(self):
        return v2p(self.cv_tv_au, self.p_tv_au, self.desired_pressures)

    @LazyProperty
    def cv_tp_jmolk(self):
        return ry_to_j_mol(self.cv_tp_au) / self.formula_unit_number

    @LazyProperty
    def gamma_tp(self):
        return gruneisen_parameter(self.v_tp_bohr3, self.bt_tp_au, self.alpha_tp, self.cv_tp_au)

    @LazyProperty
    def bs_tp_au(self):
        return adiabatic_bulk_modulus(self.bt_tp_au, self.alpha_tp, self.gamma_tp, self.temperature_array)

    @LazyProperty
    def bs_tp_gpa(self):
        return ry_b3_to_gpa(self.bs_tp_au)

    @LazyProperty
    def cp_tp_au(self):
        return isobaric_heat_capacity(self.cv_tp_au, self.alpha_tp, self.gamma_tp, self.temperature_array)

    @LazyProperty
    def cp_tp_jmolk(self):
        return isobaric_heat_capacity(self.cv_tp_jmolk, self.alpha_tp, self.gamma_tp, self.temperature_array)


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
            nm_tmp, volumes_tmp, static_energies_tmp, freq_tmp, weights_tmp = read_input(
                inp)

            if not qha.tools.is_monotonic_decreasing(volumes_tmp):
                # TODO: Clean this sentence
                save_to_output(
                    self.settings['qha_output'], "Check the input file to make sure the volume decreases")
                raise ValueError(
                    "Check the input file to make sure the volumes are monotonic decreasing!")

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
            raise RuntimeError(
                "All the formula unit number in all inputs should be the same!")

        if len(volumes.shape) == 1:
            raise RuntimeError(
                "All configurations should have same number of volumes!")

        # Choose any of them since they are all the same
        self._formula_unit_number = formula_unit_numbers[0]
        self._volumes = volumes
        self._static_energies = static_energies
        self._frequencies = frequencies
        self._q_weights = q_weights

    @LazyProperty
    def vib_ry(self):
        # We grep all the arguments once since they are being invoked for thousands of times, and will be an overhead.
        args = self.degeneracies, self.q_weights, self.static_energies, self._volumes, self.frequencies, \
            self.settings['static_only']

        mat = np.empty((self.temperature_array.size, self._volumes.shape[1]))
        for i, t in enumerate(self.temperature_array):
            mat[i] = different_phonon_dos.PartitionFunction(
                t, *(arg for arg in args)).get_free_energies()

        return mat


class SamePhDOSCalculator(DifferentPhDOSCalculator):
    def __init__(self, user_settings):
        super().__init__(user_settings)

    @LazyProperty
    def vib_ry(self):
        args = self.degeneracies, self.q_weights[0], self.static_energies, self._volumes, self.frequencies[0], \
            self.settings['static_only'], self.settings['order']
        mat = np.empty((self.temperature_array.size, self._volumes.shape[1]))

        for i, t in enumerate(self.temperature_array):
            mat[i] = same_phonon_dos.FreeEnergy(
                t, *(arg for arg in args)).get_free_energies()
        return mat
