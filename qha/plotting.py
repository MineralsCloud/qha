#!/usr/bin/env python3
"""
.. module
   :platform: Unix, Windows, Mac, Linux
   :synopsis:
.. moduleauthor:: Tian Qin <qinxx197@umn.edu>
.. moduleauthor:: Qi Zhang <qz2280@columbia.edu>
"""
import matplotlib

matplotlib.use('Agg')
import matplotlib.pylab as plt
import pandas as pd
import seaborn as sns
import pathlib
import numpy as np

# ===================== What can be exported? =====================
__all__ = ['Plotter']


class Plotter:
    def __init__(self, user_settings):
        self.user_settings = user_settings
        self.results_folder = pathlib.Path(self.user_settings['output_directory'])

    def plot2file(self, plot_what):
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

    @staticmethod
    def plot_to_file():
        size_small = 12
        size_medium = 14
        size_big = 16
        fontweight = 'normal'  # normal, bold, bolder, lighter

        # Defind the font size
        plt.rcParams['font.size'] = size_small
        plt.rcParams['font.weight'] = fontweight
        plt.rcParams['axes.titlesize'] = size_medium
        plt.rcParams['axes.labelsize'] = size_medium
        plt.rcParams['legend.fontsize'] = size_small
        plt.rcParams['figure.titlesize'] = size_big

        plt.rcParams['axes.linewidth'] = 1.5
        plt.rcParams['xtick.major.size'] = 6
        plt.rcParams['xtick.minor.size'] = 3
        plt.rcParams['ytick.major.size'] = 6
        plt.rcParams['ytick.minor.size'] = 3
        plt.rcParams['lines.linewidth'] = 2

        # Define the x and y tick features
        plt.rcParams['xtick.labelsize'] = size_small
        plt.rcParams['ytick.labelsize'] = size_small
        plt.rcParams['xtick.direction'] = 'in'
        plt.rcParams['ytick.direction'] = 'in'
        plt.rcParams['xtick.minor.visible'] = True
        plt.rcParams['ytick.minor.visible'] = True
        # Define the default figure size in inches
        plt.rcParams['figure.figsize'] = [8, 6]
        # Define Figures overall properties
        plt.rcParams['figure.dpi'] = 300

        plt.figure()

    @staticmethod
    def save_fig(ax, fig_name):
        fig = ax.get_figure()
        fig_name_pdf = str(fig_name) + '.pdf'
        fig.savefig(fig_name_pdf, format='pdf', dpi=300, bbox_inches='tight')

    def plot_thermal_expansion(self):
        f_alpha = self.user_settings['alpha']
        alpha = pd.read_csv(f_alpha, sep='\s+', index_col='T(K)\P(GPa)')
        self.plot_to_file()
        ax = alpha.plot(figsize=(6, 5), color=sns.color_palette("Reds", len(alpha.columns)))
        ax.set_xlabel('Temperature (K)')
        ax.set_ylabel('Thermal Expansion')
        ax.legend(frameon=False, bbox_to_anchor=(1.02, 1), loc='upper left', title="P (GPa)")
        ax.set_xlim(alpha.index.min(), alpha.index.max())
        ax.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
        fig_name = self.results_folder / 'alpha_T'
        self.save_fig(ax, fig_name)

    def plot_isothermal_bulk_modulus(self):
        f_isothermal_bulk_modulus = self.user_settings['Bt']
        btp = pd.read_csv(f_isothermal_bulk_modulus, sep='\s+', index_col='T(K)\P(GPa)')
        self.plot_to_file()
        ax = btp.plot(y=btp.columns[0], use_index=True, figsize=(6, 5), color='k')
        ax.set_xlabel('Temperature (K)')
        ax.set_ylabel('Isothermal Bulk Modulus (GPa)')
        ax.legend(frameon=True, loc='best', title="P (GPa)")
        ax.set_xlim(btp.index.min(), btp.index.max())
        fig_name = self.results_folder / 'Bt_T'
        self.save_fig(ax, fig_name)

    def plot_pressure_specific_heat_capacity(self):
        f_cp = self.user_settings['Cp']
        cp = pd.read_csv(f_cp, sep='\s+', index_col='T(K)\P(GPa)')
        self.plot_to_file()
        ax = cp.plot(figsize=(6, 5), color=sns.color_palette("Blues", len(cp.columns)))
        ax.set_xlabel('Temperature (K)')
        ax.set_ylabel('Cp (J/mol K)')
        ax.legend(frameon=False, bbox_to_anchor=(1.02, 1), loc='upper left', title="P (GPa)")
        ax.set_xlim(cp.index.min(), cp.index[:-2].max())
        ax.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
        fig_name = self.results_folder / 'Cp_T'
        self.save_fig(ax, fig_name)

    def plot_gruneisen_parameter(self):
        f_gamma = self.user_settings['gamma']
        gamma = pd.read_csv(f_gamma, sep='\s+', index_col='T(K)\P(GPa)')
        self.plot_to_file()
        ax = gamma.plot(figsize=(6, 5), color=sns.color_palette("Greens", len(gamma.columns)))
        ax.set_xlabel('Temperature (K)')
        ax.set_ylabel('Gruneisen Parameter')
        ax.legend(frameon=False, bbox_to_anchor=(1.02, 1), loc='upper left', title="P (GPa)")
        ax.set_xlim(gamma.index.min(), gamma.index[:-2].max())
        ax.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
        fig_name = self.results_folder / 'gamma_T'
        self.save_fig(ax, fig_name)

    def plot_gibbs_free_energy(self):
        f_gibbs = self.user_settings['G']
        gibbs = pd.read_csv(f_gibbs, sep='\s+', index_col='T(K)\P(GPa)')
        self.plot_to_file()
        ax = gibbs.plot(figsize=(6, 5), color=sns.color_palette("binary", len(gibbs.columns)))
        ax.set_xlabel('Temperature (K)')
        ax.set_ylabel('Gibbs Free Energy (ev)')
        ax.legend(frameon=False, bbox_to_anchor=(1.02, 1), loc='upper left', title="P (GPa)")
        ax.set_xlim(gibbs.index.min(), gibbs.index.max())
        fig_name = self.results_folder / 'G_T'
        self.save_fig(ax, fig_name)

    def plot_volume(self):
        f_volume = self.user_settings['V']
        volume = pd.read_csv(f_volume, sep='\s+', index_col='T(K)\P(GPa)')
        self.plot_to_file()
        ax = volume.plot(figsize=(6, 5), color=sns.color_palette("Oranges", len(volume.columns)))
        ax.set_xlabel('Temperature (K)')
        ax.set_ylabel(r'Volume ($\AA^3$)')
        ax.legend(frameon=False, bbox_to_anchor=(1.02, 1), loc='upper left', title="P (GPa)")
        ax.set_xlim(volume.index.min(), volume.index.max())
        fig_name = self.results_folder / 'V_T'
        self.save_fig(ax, fig_name)

    def fv_pv(self):
        temperature_sample: list = self.user_settings['T4FV']
        f_min = []
        v_f_min = []

        f_fitted_volume = self.user_settings['f_tv_fitted']
        volume_tv = pd.read_csv(f_fitted_volume, sep='\s+', index_col='T(K)\V(A^3)')
        volume_tv.index = volume_tv.index.map(str)
        volume_vt = volume_tv.T
        volume_vt.index = volume_vt.index.map(float)
        volume_t = volume_vt[temperature_sample]
        volume_v_grid = np.asarray(volume_vt.index, float)

        f_nonfitted_volume = self.user_settings['f_tv_non_fitted']
        volume_nonfitted_tv = pd.read_csv(f_nonfitted_volume, sep='\s+', index_col='T(K)\V(A^3)')
        volume_nonfitted_tv.index = volume_nonfitted_tv.index.map(str)
        volume_nonfitted_vt = volume_nonfitted_tv.T
        volume_nonfitted_vt.index = volume_nonfitted_vt.index.map(float)
        volume_nonfitted_t = volume_nonfitted_vt[temperature_sample]

        f_p_volume = self.user_settings['p_tv_gpa']
        p_volume_tv = pd.read_csv(f_p_volume, sep='\s+', index_col='T(K)\V(A^3)')
        p_volume_tv.index = p_volume_tv.index.map(str)
        p_volume_vt = p_volume_tv.T
        p_volume_vt.index = p_volume_vt.index.map(float)
        p_volume_t = p_volume_vt[temperature_sample]

        # Get the 'V0' and 'E0' for selected Temperatures
        for t in temperature_sample:
            f_min.append(float(volume_vt[t].min()))
            v_f_min.append(float(volume_vt[t].idxmin()))

        self.plot_to_file()

        fig, axes = plt.subplots(nrows=1, ncols=2)
        volume_t.plot(ax=axes[0], style='b-')
        volume_nonfitted_t.plot(ax=axes[0], style='ko')
        axes[0].plot(v_f_min, f_min, 'ro-', label=None)

        axes[0].set_xlabel(r'Volume ($\AA$)')
        axes[0].set_ylabel('Helmholtz Free Energy (eV)')
        axes[0].legend().set_visible(False)
        axes[0].set_xlim(volume_v_grid.min(), volume_v_grid.max())
        for t in temperature_sample:
            x, y = 1.002 * float(volume_v_grid.max()), volume_vt[t].tolist()[0]
            axes[0].text(x, y, str(t) + ' K', fontsize=8)

        axes[1].axhline(y=self.user_settings['DESIRED_PRESSURES_GPa'][0], color='whitesmoke')
        axes[1].axhline(y=self.user_settings['DESIRED_PRESSURES_GPa'][-1], color='whitesmoke')
        p_volume_t.plot(ax=axes[1], style='k-')

        axes[1].set_xlabel(r'Volume ($\AA$)')
        axes[1].set_ylabel('Pressure (GPa)')
        axes[1].legend().set_visible(False)
        axes[1].set_xlim(volume_v_grid.min(), volume_v_grid.max())

        fig.tight_layout(w_pad=3.2, h_pad=0)
        fig_name_pdf = str(self.results_folder / 'FVT_PVT.pdf')
        fig.savefig(fig_name_pdf, format='pdf', dpi=300, bbox_inches='tight')
