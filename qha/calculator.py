#!/usr/bin/env python3

import numpy as np
import pandas as pd
from lazy_property import LazyProperty

import qha.multi_configurations.different_vdos as diff_vdos
import qha.multi_configurations.same_vdos as same_vdos
import qha.tools
from qha.grid_interpolation import RefineGrid
from qha.output import save_to_output
from qha.readers import read_input
from qha.single_configuration import free_energy
from qha.thermodynamics import *
from qha.unit_conversion import gpa_to_ry_b3, ry_b3_to_gpa, b3_to_a3, ry_to_j_mol, ry_to_ev
from qha.v2p import v2p


class QHACalculator:
    def __init__(self, user_settings):

        self.settings = user_settings

        for keynames in ['multi_config_same_vdos', 'multi_config', 'input', 'volume_energies',
                         'config_degeneracy',
                         'calculate', 'static_only', 'energy_unit',
                         'NT', 'DT', 'DT_SAMPLE',
                         'P_MIN', 'NTV', 'DELTA_P', 'DELTA_P_SAMPLE',
                         'calculate', 'volume_ratio', 'order', 'p_min_modifier',
                         'T4FV', 'results_folder', 'plot_calculation', 'show_more_output', 'qha_output']:
            try:
                setattr(self, keynames, self.settings[keynames])
            except KeyError:
                continue

    @LazyProperty
    def finer_volume_ftv(self):
        if hasattr(self, 'volume_ratio'):
            finer_volumes, ftv, v_ratio = RefineGrid(getattr(self, 'P_MIN') - getattr(self, 'p_min_modifier'),
                                                     getattr(self, 'NTV'), option=getattr(self, 'order')).refine_grids(
                self.volumes, self.vib_ry,
                ratio=self.volume_ratio)
        else:
            finer_volumes, ftv, v_ratio = RefineGrid(getattr(self, 'P_MIN') - getattr(self, 'p_min_modifier'),
                                                     getattr(self, 'NTV'), option=getattr(self, 'order')).refine_grids(
                self.volumes, self.vib_ry)

        return finer_volumes, ftv, v_ratio

    @LazyProperty
    def finer_volumes_au(self):
        return self.finer_volume_ftv[0]

    @LazyProperty
    def f_tv_au(self):
        return self.finer_volume_ftv[1]

    @LazyProperty
    def v_ratio(self):
        return self.finer_volume_ftv[2]

    @LazyProperty
    def pot(self):
        return thermodynamic_potentials(self.temperature_array, self.finer_volumes_au, self.f_tv_au,
                                        self.p_tv_au)

    @LazyProperty
    def get_essential_data(self):
        nm, volumes, static_energies, freq, weights = read_input(getattr(self, 'input'))
        if not qha.tools.is_monotonic_decreasing(volumes):
            save_to_output(getattr(self, 'qha_output'), "Check the input file to make sure the volume decreases")
            raise ValueError("Check the input file to make sure the volume decreases")
        return nm, volumes, static_energies, freq, weights

    @LazyProperty
    def nm(self):
        return self.get_essential_data[0]

    @LazyProperty
    def volumes(self):
        return self.get_essential_data[1]

    @LazyProperty
    def static_energies(self):
        return self.get_essential_data[2]

    @LazyProperty
    def freq(self):
        return self.get_essential_data[3]

    @LazyProperty
    def weights(self):
        return self.get_essential_data[4]

    @LazyProperty
    def temperature_array(self):
        # Normally, last 2 termperature points in Cp is not accurate,
        # Here 4 more points are added for calculation, but will remove these points at the output files.
        return qha.tools.arange(0, getattr(self, 'NT') + 4, getattr(self, 'DT'))

    @LazyProperty
    def temperature_sample_array(self):
        return self.temperature_array[0::int(getattr(self, 'DT_SAMPLE') / getattr(self, 'DT'))]

    @LazyProperty
    def desired_pressures_gpa(self):
        return qha.tools.arange(getattr(self, 'P_MIN'), getattr(self, 'NTV'), getattr(self, 'DELTA_P'))

    @LazyProperty
    def desired_pressures(self):
        return gpa_to_ry_b3(self.desired_pressures_gpa)

    @LazyProperty
    def pressure_sample_array(self):
        return self.desired_pressures_gpa[0::int(getattr(self, 'DELTA_P_SAMPLE') / getattr(self, 'DELTA_P'))]

    @LazyProperty
    def vib_ry(self):
        return np.array(
            [free_energy(t, self.weights, self.static_energies, self.freq, getattr(self, 'static_only')) for t in
             self.temperature_array])

    @LazyProperty
    def finer_volumes_ang3(self):
        return b3_to_a3(self.finer_volumes_au)

    @LazyProperty
    def vib_ev(self):
        return ry_to_ev(self.vib_ry)

    @LazyProperty
    def volumes_ang3(self):
        return b3_to_a3(self.volumes)

    def desired_pressure_status(self):
        if getattr(self, 'show_more_output'):
            save_to_output(getattr(self, 'qha_output'),
                           "The pressure range can be dealt with: [%6.2f to %6.2f ] GPa" % (
                               self.p_tv_gpa[:, 0].max(), self.p_tv_gpa[:, -1].min()))

        if self.p_tv_gpa[:, -1].min() < self.desired_pressures_gpa.max():
            ntv_max = int((self.p_tv_gpa[:, -1].min() - self.desired_pressures_gpa.min()) / getattr(self, 'DELTA_P'))
            save_to_output(getattr(self, 'qha_output'),
                           "\n\n!!!ATTENTION!!!\n"
                           "DESIRED PRESSURE is too high (NTV is too large)!!!\n"
                           "qha results might not be right!!!\n"
                           "please reduce the NTV accordingly, for example, try to set NTV < %4d.\n" % ntv_max)
            raise ValueError("DESIRED PRESSURE is too high (NTV is too large), qha results might not be right!  ")

        return 'DESIRED PRESSURE setting is okay!'

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
        return self.pot['U']

    @LazyProperty
    def u_tp_au(self):
        return v2p(self.u_tv_au, self.p_tv_au, self.desired_pressures)

    @LazyProperty
    def u_tp_ev(self):
        return ry_to_ev(self.u_tp_au)

    @LazyProperty
    def h_tv_au(self):
        return self.pot['H']

    @LazyProperty
    def h_tp_au(self):
        return v2p(self.h_tv_au, self.p_tv_au, self.desired_pressures)

    @LazyProperty
    def h_tp_ev(self):
        return ry_to_ev(self.h_tp_au)

    @LazyProperty
    def g_tv_au(self):
        return self.pot['G']

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
        return ry_to_j_mol(self.cv_tp_au) / self.nm

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


class QHASameVdosCalculator(QHACalculator):
    def __init__(self, user_settings):
        super().__init__(user_settings)
        self.volume_energy, self.degeneracy = self.get_config_energy_degeneracy()

    def get_config_energy_degeneracy(self):
        volume_energy = pd.read_csv(getattr(self, 'volume_energies'), sep='\s+', index_col='volume')
        degeneracy = pd.read_csv(getattr(self, 'config_degeneracy'), sep='\s+', index_col='config')
        return volume_energy, degeneracy['degeneracy'].tolist()

    @LazyProperty
    def vib_ry(self):
        return np.array(
            [same_vdos.FreeEnergy(t, self.volume_energy.as_matrix(), self.degeneracy, self.weights, self.freq).total for
             t in
             self.temperature_array])


class QHAMultiConfigCalculator(QHACalculator):
    def __init__(self, user_settings):
        super().__init__(user_settings)

    def essential_data(self):
        essentials = pd.read_csv(getattr(self, 'config_degeneracy'), sep='\s+', dtype={'config': str})
        essentials.set_index('config', inplace=True)
        config_file_name = list(map(lambda d: getattr(self, 'input') + '{0}'.format(d), essentials.index.tolist()))
        return essentials['degeneracy'].tolist(), config_file_name

    @LazyProperty
    def degeneracy(self):
        return self.essential_data()[0]

    @LazyProperty
    def config_file_name(self):
        return self.essential_data()[1]

    @LazyProperty
    def get_essential_data_config(self):
        nm = []
        volumes = []
        static_energies = []
        freq = []
        weights = []
        for fn_input in self.config_file_name:
            nm_tmp, volumes_tmp, static_energies_tmp, freq_tmp, weights_tmp = read_input(fn_input)
            if not qha.tools.is_monotonic_decreasing(volumes):
                save_to_output(getattr(self, 'qha_output'), "Check the input file to make sure the volume decreases")
                raise ValueError("Check the input file to make sure the volume decreases")

            nm.append(nm_tmp)
            volumes.append(volumes_tmp)
            static_energies.append(static_energies_tmp)
            freq.append(freq_tmp)
            weights.append(weights_tmp)

        nm = np.array(nm)
        volumes = np.array(volumes)
        static_energies = np.array(static_energies)
        freq = np.array(freq)
        weights = np.array(weights)

        return nm, volumes, static_energies, freq, weights

    @LazyProperty
    def nm_configs(self):
        return self.get_essential_data_config[0]

    @LazyProperty
    def volumes_configs(self):
        return self.get_essential_data_config[1]

    @LazyProperty
    def static_energies_configs(self):
        return self.get_essential_data_config[2]

    @LazyProperty
    def freq_configs(self):
        return self.get_essential_data_config[3]

    @LazyProperty
    def weights_configs(self):
        return self.get_essential_data_config[4]

    @LazyProperty
    def nm(self):
        return self.nm_configs[0]

    @LazyProperty
    def volumes(self):
        return self.volumes_configs[0]

    @LazyProperty
    def vib_ry(self):
        partition_function_free_energy = np.array(
            [diff_vdos.PartitionFunction(t, self.static_energies_configs, self.degeneracy, self.weights_configs,
                                         self.freq_configs, self.volumes_configs,
                                         getattr(self, 'static_only')).derive_free_energy
             for t in self.temperature_array])
        return partition_function_free_energy
