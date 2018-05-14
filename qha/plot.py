#!/usr/bin/env python3
"""
:mod:`` --
========================================

.. module
   :platform: Unix, Windows, Mac, Linux
   :synopsis:
.. moduleauthor:: Tian Qin <qinxx197@umn.edu>
.. moduleauthor:: Qi Zhang <qz2280@columbia.edu>
"""

import matplotlib.pylab as plt
import pandas as pd
import seaborn as sns

# ===================== What can be exported? =====================
__all__ = ['Plotter']


class Plotter:
    def __init__(self, user_settings):
        # self.folder = 'results/'
        self.user_settings = user_settings
        self.results_folder = self.user_settings['output_directory']
        self.plot_flag = self.user_settings['plot_results']
        # self.color_cycle = cycle(['b','r','g','y','k'])

    def plot2file(self, plot_what):
        if self.plot_flag in [True, 'T', 't']:
            if plot_what == 'alpha':
                self.plot_thermal_expansion()
            if plot_what == 'gamma':
                self.plot_gruneisen_parameter()
            if plot_what == 'Cp':
                self.plot_pressure_specific_heat_capacity()
            if plot_what == 'Bt':
                self.plot_isothermal_bulk_modulus()
            if plot_what == 'G':
                self.plot_gibbs_free_energy()
            if plot_what == 'V':
                self.plot_volume()

    def plot_to_file(self):
        SMALL_SIZE = 12
        MEDIUM_SIZE = 14
        BIGGER_SIZE = 16
        fontweight = 'normal'  # normal, bold, bolder, lighter

        # Defind the font size
        plt.rcParams['font.size'] = SMALL_SIZE
        plt.rcParams['font.weight'] = fontweight
        plt.rcParams['axes.titlesize'] = MEDIUM_SIZE  # fontsize of the axes title
        plt.rcParams['axes.labelsize'] = MEDIUM_SIZE  # fontsize of the x and y labels
        plt.rcParams['legend.fontsize'] = SMALL_SIZE  # legend fontsize
        plt.rcParams['figure.titlesize'] = BIGGER_SIZE  # fontsize of the figure title

        plt.rcParams['axes.linewidth'] = 1.5
        plt.rcParams['xtick.major.size'] = 6
        plt.rcParams['xtick.minor.size'] = 3
        plt.rcParams['ytick.major.size'] = 6
        plt.rcParams['ytick.minor.size'] = 3
        plt.rcParams['lines.linewidth'] = 2

        # Define the x and y tick features
        plt.rcParams['xtick.labelsize'] = SMALL_SIZE  # fontsize of the tick labels
        plt.rcParams['ytick.labelsize'] = SMALL_SIZE  # fontsize of the tick labels
        plt.rcParams['xtick.direction'] = 'in'  # in, out, or inout
        plt.rcParams['ytick.direction'] = 'in'  # in, out, or inout
        plt.rcParams['xtick.minor.visible'] = True
        plt.rcParams['ytick.minor.visible'] = True
        # Define the default figure size in inches
        plt.rcParams['figure.figsize'] = [8, 6]  # figure size in inches
        # Define Figures overall properties
        plt.rcParams['figure.dpi'] = 300

        plt.figure()

    @staticmethod
    def save_fig(ax, fig_name):
        fig = ax.get_figure()
        fig_name_pdf = fig_name + '.pdf'
        fig.savefig(fig_name_pdf, format='pdf', dpi=300, bbox_inches='tight')

    def plot_thermal_expansion(self):
        self.f_alpha = self.user_settings['alpha']
        alpha = pd.read_csv(self.f_alpha, sep='\s+', index_col='T(K)\P(GPa)')
        self.plot_to_file()
        ax = alpha.plot(figsize=(6, 5), color=sns.color_palette("Reds", len(alpha.columns)))  # 'cubehelix'
        ax.set_xlabel('Temperature (K)')
        ax.set_ylabel('Thermal Expansion')
        ax.legend(frameon=False, bbox_to_anchor=(1.02, 1), loc='upper left', title="P (GPa)")  # fontsize=10,
        ax.set_xlim(alpha.index.min(), alpha.index.max())
        ax.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
        fig_name = self.results_folder + 'alpha' + '_T'
        # fig_name = 'results/thermal_expansion_T'
        self.save_fig(ax, fig_name)

    def plot_isothermal_bulk_modulus(self):
        self.f_isothermal_bulk_modulus = self.user_settings['Bt']
        btp = pd.read_csv(self.f_isothermal_bulk_modulus, sep='\s+', index_col='T(K)\P(GPa)')
        self.plot_to_file()
        ax = btp.plot(y=btp.columns[0], use_index=True, figsize=(6, 5), color='k')
        ax.set_xlabel('Temperature (K)')
        ax.set_ylabel('Isothermal Bulk Modulus (GPa)')
        # hide the legend, use ax.legend().set_visible(False)
        ax.legend(frameon=True, loc='best', title="P (GPa)")
        ax.set_xlim(btp.index.min(), btp.index.max())
        # fig_name = 'results/isothermal_bulk_modulus_T'
        fig_name = self.results_folder + 'Bt' + '_T'
        self.save_fig(ax, fig_name)

    def plot_pressure_specific_heat_capacity(self):
        self.f_cp = self.user_settings['Cp']
        cp = pd.read_csv(self.f_cp, sep='\s+', index_col='T(K)\P(GPa)')
        self.plot_to_file()
        ax = cp.plot(figsize=(6, 5), color=sns.color_palette("Blues", len(cp.columns)))
        ax.set_xlabel('Temperature (K)')
        ax.set_ylabel('Cp (J/mol K)')
        ax.legend(frameon=False, bbox_to_anchor=(1.02, 1), loc='upper left', title="P (GPa)")  # fontsize=10,
        ax.set_xlim(cp.index.min(), cp.index[:-2].max())
        ax.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
        fig_name = self.results_folder + 'Cp' + '_T'
        self.save_fig(ax, fig_name)

    def plot_gruneisen_parameter(self):
        self.f_gamma = self.user_settings['gamma']
        gamma = pd.read_csv(self.f_gamma, sep='\s+', index_col='T(K)\P(GPa)')
        self.plot_to_file()
        ax = gamma.plot(figsize=(6, 5), color=sns.color_palette("Greens", len(gamma.columns)))
        ax.set_xlabel('Temperature (K)')
        ax.set_ylabel('Gruneisen Parameter')
        ax.legend(frameon=False, bbox_to_anchor=(1.02, 1), loc='upper left', title="P (GPa)")  # fontsize=10,
        ax.set_xlim(gamma.index.min(), gamma.index[:-2].max())
        ax.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
        fig_name = self.results_folder + 'gamma' + '_T'
        # fig_name = 'results/gruneisen_parameter_T'
        self.save_fig(ax, fig_name)

    def plot_gibbs_free_energy(self):
        self.f_gibbs = self.user_settings['G']
        gibbs = pd.read_csv(self.f_gibbs, sep='\s+', index_col='T(K)\P(GPa)')
        self.plot_to_file()
        ax = gibbs.plot(figsize=(6, 5), color=sns.color_palette("binary", len(gibbs.columns)))
        ax.set_xlabel('Temperature (K)')
        ax.set_ylabel('Gibbs Free Energy (ev)')
        ax.legend(frameon=False, bbox_to_anchor=(1.02, 1), loc='upper left', title="P (GPa)")  # fontsize=10,
        ax.set_xlim(gibbs.index.min(), gibbs.index.max())
        fig_name = 'results/gibbs_free_energy_T'
        fig_name = self.results_folder + 'G_T'
        self.save_fig(ax, fig_name)

    def plot_volume(self):
        self.f_volume = self.user_settings['V']
        volume = pd.read_csv(self.f_volume, sep='\s+', index_col='T(K)\P(GPa)')
        self.plot_to_file()
        ax = volume.plot(figsize=(6, 5),
                         color=sns.color_palette("Oranges", len(volume.columns)))  # ,y='0.0', use_index=True
        ax.set_xlabel('Temperature (K)')
        ax.set_ylabel(r'Volume ($\AA^3$)')
        ax.legend(frameon=False, bbox_to_anchor=(1.02, 1), loc='upper left', title="P (GPa)")  # fontsize=10,
        ax.set_xlim(volume.index.min(), volume.index.max())
        fig_name = self.results_folder + 'V' + '_T'
        self.save_fig(ax, fig_name)

    def fv_pv(self):
        T_sample: list = self.user_settings['T4FV']
        f_min = []
        v_f_min = []

        self.f_fitted_volume = self.user_settings['f_tv_fitted']
        volume = pd.read_csv(self.f_fitted_volume, sep='\s+', index_col='V(A^3)\T(K)')
        volume_t = volume[T_sample]

        self.f_nonfitted_volume = self.user_settings['f_tv_non_fitted']
        volume_nonfitted = pd.read_csv(self.f_nonfitted_volume, sep='\s+', index_col='V(A^3)\T(K)')
        volume_nonfitted_t = volume_nonfitted[T_sample]

        self.f_p_volume = self.user_settings['p_tv_gpa']
        p_volume = pd.read_csv(self.f_p_volume, sep='\s+', index_col='V(A^3)\T(K)')
        p_volume_t = p_volume[T_sample]

        # Get the 'V0' and 'E0' for selected Temperatures
        for t in T_sample:
            f_min.append(float(volume[t].min()))
            v_f_min.append(float(volume[t].idxmin()))

        self.plot_to_file()

        fig, axes = plt.subplots(nrows=1, ncols=2)
        volume_t.plot(ax=axes[0], style='b-')  # use_index=True, y=T_sample,
        volume_nonfitted_t.plot(ax=axes[0], style='ko')  # ,, use_index=True, y=T_sample,
        axes[0].plot(v_f_min, f_min, 'ro-', label=None)

        axes[0].set_xlabel(r'Volume ($\AA$)')
        axes[0].set_ylabel('Helmholtz Free Energy (eV)')
        axes[0].legend().set_visible(False)
        axes[0].set_xlim(volume.index.min(), volume.index.max())
        for t in T_sample:
            x, y = 1.002 * volume.index.max(), volume[t].tolist()[0]
            axes[0].text(x, y, t + ' K', fontsize=8)

        axes[1].axhline(y=self.user_settings['DESIRED_PRESSURES_GPa'][0], color='whitesmoke')
        axes[1].axhline(y=self.user_settings['DESIRED_PRESSURES_GPa'][-1], color='whitesmoke')
        # p_volume.plot(ax=axes[1], use_index=True, y=T_sample, style='k-')
        p_volume_t.plot(ax=axes[1], style='k-')  # use_index=True, y=T_sample,

        axes[1].set_xlabel(r'Volume ($\AA$)')
        axes[1].set_ylabel('Pressure (GPa)')
        axes[1].legend().set_visible(False)
        axes[1].set_xlim(volume.index.min(), volume.index.max())

        fig.tight_layout(w_pad=3.2, h_pad=0)

        fig_name = self.results_folder + 'FVT_PVT'

        fig_name_pdf = fig_name + '.pdf'
        fig.savefig(fig_name_pdf, format='pdf', dpi=300, bbox_inches='tight')
