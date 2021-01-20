#!/usr/bin/env python3
"""
.. module output
   :platform: Unix, Windows, Mac, Linux
   :synopsis: doc
.. moduleauthor:: Tian Qin <qinxx197@umn.edu>
.. moduleauthor:: Qi Zhang <qz2280@columbia.edu>
"""

import textwrap
from datetime import datetime

import pandas as pd


def save_to_output(fn_output, text):
    with open(fn_output, 'a') as f:
        f.write(text + '\n')


def save_x_tp(df, t, desired_pressures_gpa, p_sample_gpa, outfile_name):
    # To fix the last 2 temperature points of Cp is not accurate, we added 4 temperature points,
    # Now to get rid of the added temperature points before saving calculated properties into files.
    df = pd.DataFrame(df, index=t, columns=desired_pressures_gpa).iloc[:-4, :]
    df.columns.name = 'T(K)\P(GPa)'
    sample = df.loc[:, df.columns.isin(p_sample_gpa)]
    with open(outfile_name, 'w') as f:
        f.write(sample.to_string())


def save_x_pt(df, t, desired_pressures_gpa, t_sample, outfile_name):
    # To fix the last 2 temperature points of Cp is not accurate, we added 4 temperature points,
    # Now to get rid of the added temperature points before saving calculated properties into files.
    df = pd.DataFrame(df[:-4].T, index=desired_pressures_gpa, columns=t[:-4])
    df.columns.name = 'P(GPa)\T(K)'
    sample = df.loc[:, df.columns.isin(t_sample)]
    with open(outfile_name, 'w') as f:
        f.write(sample.to_string())


def save_x_vt(x, t, volume_grid, t_sample, outfile_name):
    df = pd.DataFrame(x.T, index=volume_grid, columns=t)
    df.columns.name = 'V(A^3)\T(K)'
    sample = df.loc[:, df.columns.isin(t_sample)]
    with open(outfile_name, 'w') as f:
        f.write(sample.to_string())


def save_x_tv(x, t, volume_grid, t_sample, outfile_name):
    df = pd.DataFrame(x, index=t, columns=volume_grid).iloc[:-4, :]
    df.columns.name = 'T(K)\V(A^3)'
    sample = df.loc[df.index.isin(t_sample[:-4]), :]
    with open(outfile_name, 'w') as f:
        f.write(sample.to_string())


def make_starting_string() -> str:
    return textwrap.dedent("""\
        ============================================================
        Current time: {0:%Y-%m-%d %H:%M:%S}
        """.format(datetime.utcnow()))


def make_tp_info(min_temperature, max_temperature, min_pressure, max_pressure):
    return textwrap.dedent("""\
        ------------------------------------------------------------
         Desired T range:    {0:6.2f} to {1:6.2f}  K
         Desired P range:    {2:6.2f} to {3:6.2f}  GPa
        ------------------------------------------------------------
        """.format(min_temperature, max_temperature, min_pressure, max_pressure))


def make_ending_string(time_elapsed) -> str:
    return textwrap.dedent("""\
        ------------------------------------------------------------
        Total elapsed time is: {0:8.2f} seconds
        Thanks for using QHA code, have a nice one :)
        ============================================================
        """.format(time_elapsed))
