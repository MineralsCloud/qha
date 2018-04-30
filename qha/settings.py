#!/usr/bin/env python3
"""
:mod:`settings` -- Data model for user computational settings
=============================================================

.. module
   :platform: Unix, Windows, Mac, Linux
   :synopsis: In this module, we give a simple computational settings ``DEFAULT_SETTING``, which will
   be used by default in the following calculation, if the users do not specify settings themselves.
   If they want, they can write some settings in a Python ``dictionary`` object, or save it
   in some Json files.
.. moduleauthor:: Tian Qin <qinxx197@umn.edu>
.. moduleauthor:: Qi Zhang <qz2280@columbia.edu>
"""

import collections
from typing import Union, Tuple, Dict, Any

import yaml

# ===================== What can be exported? =====================
__all__ = ['DEFAULT_SETTING', 'Settings', 'from_yaml']

DEFAULT_SETTING: Dict[str, Any] = {
    'energy_unit': 'ry',
    'length_unit': 'angstrom',
    'order': 3,  # BM fitting order, can be 3, 4 or 5, normally, 3rd order is sufficient.
    'p_min_modifier': 1.0,
    'target': 'parallel',
    'DT_SAMPLE': 10,
    'DELTA_P': 0.1,
    'DELTA_P_SAMPLE': 1,
    'static_only': False,
    'same_phonon_dos': False,
    # output setting
    'output_directory': './results/',
    'T4FV': ['0', '300'],
    'plot_results': False,
    'high_verbosity': False
}


class Settings(collections.ChainMap):
    def __init__(self, *user_settings: Union[Dict[str, Any], Tuple[Dict[str, Any], ...]]):
        super().__init__(*user_settings, DEFAULT_SETTING)

    def to_yaml_file(self, filename: str):
        if not filename.endswith('.yaml'):
            filename += '.yaml'
        with open(filename, 'w') as f:
            yaml.dump(self.maps, f)


def from_yaml(filename: str):
    with open(filename, 'r') as f:
        return Settings(yaml.load(f))


global energy_unit
energy_unit = DEFAULT_SETTING['energy_unit']
