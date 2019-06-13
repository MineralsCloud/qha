#!/usr/bin/env python3
"""
.. module settings
   :platform: Unix, Windows, Mac, Linux
   :synopsis: In this module, we give a simple computational "settings" ``DEFAULT_SETTINGS``, which will
    be used by default in the following calculation, if the users do not specify "settings" themselves.
    If they want, they can write some settings in a YAML file.
.. moduleauthor:: Qi Zhang <qz2280@columbia.edu>
.. moduleauthor:: Tian Qin <qinxx197@umn.edu>
"""

import collections
from typing import Union, Tuple, Dict, Any

import yaml

# ===================== What can be exported? =====================
__all__ = ['DEFAULT_SETTINGS', 'Settings', 'from_yaml']

DEFAULT_SETTINGS: Dict[str, Any] = {
    'energy_unit': 'ry',
    'length_unit': 'angstrom',
    'order': 3,  # BM fitting order, can be 3, 4 or 5, normally, 3rd order is sufficient.
    'p_min_modifier': 1.0,
    'target': 'parallel',
    'T_MIN': 0,
    'DT_SAMPLE': 10,
    'DELTA_P': 0.1,
    'DELTA_P_SAMPLE': 1,
    'static_only': False,
    # output setting
    'output_directory': './results/',
    'T4FV': ['0', '300'],
    'high_verbosity': False
}


class Settings(collections.ChainMap):
    """
    Contains both user "settings" and default "settings", where user "settings" will override default "settings".

    The default "settings" are

    .. code-block:: python

        DEFAULT_SETTINGS: = {
            'energy_unit': 'ry',
            'length_unit': 'angstrom',
            'order': 3,
            'p_min_modifier': 1.0,
            'target': 'parallel',
            'T_MIN': 0,
            'DT_SAMPLE': 10,
            'DELTA_P': 0.1,
            'DELTA_P_SAMPLE': 1,
            'static_only': False,
            'output_directory': './results/',
            'T4FV': ['0', '300'],
            'high_verbosity': False
        }

    :param user_settings: It can be a single dictionary or a tuple of dictionaries, with strings as their keys.
    """

    def __init__(self, *user_settings: Union[Dict[str, Any], Tuple[Dict[str, Any], ...]]):
        super().__init__(*user_settings, DEFAULT_SETTINGS)

    def to_yaml_file(self, filename: str):
        if not filename.endswith('.yaml'):
            filename += '.yaml'
        with open(filename, 'w') as f:
            yaml.dump(self.maps, f)


def from_yaml(filename: str) -> Settings:
    """
    This function reads user "settings" from a YAML file, and generate a ``Settings`` class for later use.

    :param filename: The name of the YAML file.
    :return: A ``Settings`` class.
    """
    with open(filename, 'r') as f:
        return Settings(yaml.load(f, Loader=yaml.CLoader))


global energy_unit
energy_unit = DEFAULT_SETTINGS['energy_unit']
