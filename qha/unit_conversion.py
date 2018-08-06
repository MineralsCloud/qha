#!/usr/bin/env python3
"""
.. module unit_conversion
   :platform: Unix, Windows, Mac, Linux
   :synopsis: A module of packaged unit-conversion functions, with [Numba's](https://numba.pydata.org) ``@jit`` speedup.
.. moduleauthor:: Qi Zhang <qz2280@columbia.edu>
"""

from numba import float64, vectorize
from scipy.constants import physical_constants, electron_volt, angstrom, Avogadro

from qha.settings import DEFAULT_SETTINGS

# ===================== What can be exported? =====================
__all__ = [
    'j_to_ev',
    'ev_to_j',
    'gpa_to_megabar',
    'megabar_to_gpa',
    'b3_to_a3',
    'a3_to_b3',
    'eh_to_ev',
    'ev_to_eh',
    'ry_to_ev',
    'ev_to_ry',
    'j_to_eh',
    'eh_to_j',
    'eh_to_hz',
    'hz_to_eh',
    'eh_to_k',
    'k_to_eh',
    'eh_to_m_inverse',
    'm_inverse_to_eh',
    'eh_to_cm_inverse',
    'cm_inverse_to_eh',
    'ev_to_m_inverse',
    'm_inverse_to_ev',
    'ev_to_cm_inverse',
    'cm_inverse_to_ev',
    'ev_to_k',
    'k_to_ev',
    'ry_to_j',
    'j_to_ry',
    'gpa_to_ev_a3',
    'ev_a3_to_gpa',
    'gpa_to_ry_b3',
    'ry_b3_to_gpa',
    'gpa_to_ha_b3',
    'ha_b3_to_gpa',
    'ev_b3_to_gpa',
    'gpa_to_ev_b3',
    'ry_b_to_ev_a',
    'ha_b_to_ev_a',
    'ry_to_kj_mol',
    'ry_to_j_mol'
]

# ===================== Constants =====================
BOHR = physical_constants['Bohr radius'][0]
EH_EV = physical_constants['Hartree energy in eV'][0]
RY_EV = physical_constants['Rydberg constant times hc in eV'][0]
EH_J = physical_constants['hartree-joule relationship'][0]
EH_HZ = physical_constants['hartree-hertz relationship'][0]
EH_K = physical_constants['hartree-kelvin relationship'][0]
EH_M_INVERSE = physical_constants['hartree-inverse meter relationship'][0]
EV_M_INVERSE = physical_constants['electron volt-inverse meter relationship'][0]
EV_K = physical_constants['electron volt-kelvin relationship'][0]
RY_J = physical_constants['Rydberg constant times hc in J'][0]

# ===================== Settings =====================
_target = DEFAULT_SETTINGS['target']


# ===================== Functions =====================
@vectorize([float64(float64)], nopython=True, cache=True, target=_target)
def j_to_ev(value):
    """
    Convert the *value* in unit joule to electronvolt.

    :param value: The value to be converted.
    :return: The converted value.
    """
    return value / electron_volt


@vectorize([float64(float64)], nopython=True, cache=True, target=_target)
def ev_to_j(value):
    """
    Convert the *value* in unit electronvolt to joule.

    :param value: The value to be converted.
    :return: The converted value.
    """
    return value * electron_volt


@vectorize([float64(float64)], nopython=True, cache=True, target=_target)
def gpa_to_megabar(value):
    """
    Convert the *value* in unit gigapascal to megabar.

    :param value: The value to be converted.
    :return: The converted value.
    """
    return value * 0.01


@vectorize([float64(float64)], nopython=True, cache=True, target=_target)
def megabar_to_gpa(value):
    """
    Convert the *value* in unit megabar to gigapascal.

    :param value: The value to be converted.
    :return: The converted value.
    """
    return value / 0.01


@vectorize([float64(float64)], nopython=True, cache=True, target=_target)
def b3_to_a3(value):
    """
    Convert the *value* in unit cubic bohr radius to what in cubic angstrom.

    :param value: The value to be converted.
    :return: The converted value.
    """
    return value * (BOHR / angstrom) ** 3


@vectorize([float64(float64)], nopython=True, cache=True, target=_target)
def a3_to_b3(value):
    """
    Convert the *value* in unit cubic angstrom to what in cubic bohr radius.

    :param value: The value to be converted.
    :return: The converted value.
    """
    return value * (angstrom / BOHR) ** 3


@vectorize([float64(float64)], nopython=True, cache=True, target=_target)
def eh_to_ev(value):
    """
    Convert the *value* in unit hartree to electronvolt.

    :param value: The value to be converted.
    :return: The converted value.
    """
    return value * EH_EV


@vectorize([float64(float64)], nopython=True, cache=True, target=_target)
def ev_to_eh(value):
    """
    Convert the *value* in unit electronvolt to hartree.

    :param value: The value to be converted.
    :return: The converted value.
    """
    return value / EH_EV


@vectorize([float64(float64)], nopython=True, cache=True, target=_target)
def ry_to_ev(value):
    """
    Convert the *value* in unit rydberg to electronvolt.

    :param value: The value to be converted.
    :return: The converted value.
    """
    return value * RY_EV


@vectorize([float64(float64)], nopython=True, cache=True, target=_target)
def ev_to_ry(value):
    """
    Convert the *value* in unit electronvolt to rydberg.

    :param value: The value to be converted.
    :return: The converted value.
    """
    return value / RY_EV


@vectorize([float64(float64)], nopython=True, cache=True, target=_target)
def j_to_eh(value):
    """
    Convert the *value* in unit joule to hartree.

    :param value: The value to be converted.
    :return: The converted value.
    """
    return value / EH_J


@vectorize([float64(float64)], nopython=True, cache=True, target=_target)
def eh_to_j(value):
    """
    Convert the *value* in unit hartree to joule.

    :param value: The value to be converted.
    :return: The converted value.
    """
    return value * EH_J


@vectorize([float64(float64)], nopython=True, cache=True, target=_target)
def eh_to_hz(value):
    """
    Convert the *value* in unit hartree to hertz.

    :param value: The value to be converted.
    :return: The converted value.
    """
    return value * EH_HZ


@vectorize([float64(float64)], nopython=True, cache=True, target=_target)
def hz_to_eh(value):
    """
    Convert the *value* in unit hertz to hartree.

    :param value: The value to be converted.
    :return: The converted value.
    """
    return value / EH_HZ


@vectorize([float64(float64)], nopython=True, cache=True, target=_target)
def eh_to_k(value):
    """
    Convert the *value* in unit hartree to kelvin.

    :param value: The value to be converted.
    :return: The converted value.
    """
    return value * EH_K


@vectorize([float64(float64)], nopython=True, cache=True, target=_target)
def k_to_eh(value):
    """
    Convert the *value* in unit kelvin to hartree.

    :param value: The value to be converted.
    :return: The converted value.
    """
    return value / EH_K


@vectorize([float64(float64)], nopython=True, cache=True, target=_target)
def eh_to_m_inverse(value):
    """
    Convert the *value* in unit hartree to :math:`\\text{m}^{-1}`.

    :param value: The value to be converted.
    :return: The converted value.
    """
    return value * EH_M_INVERSE


@vectorize([float64(float64)], nopython=True, cache=True, target=_target)
def m_inverse_to_eh(value):
    """
    Convert the *value* in unit :math:`\\text{m}^{-1}` to hartree.

    :param value: The value to be converted.
    :return: The converted value.
    """
    return value / EH_M_INVERSE


@vectorize([float64(float64)], nopython=True, cache=True, target=_target)
def eh_to_cm_inverse(value):
    """
    Convert the *value* in unit hartree to :math:`\\text{cm}^{-1}`.

    :param value: The value to be converted.
    :return: The converted value.
    """
    return value * EH_M_INVERSE / 100


@vectorize([float64(float64)], nopython=True, cache=True, target=_target)
def cm_inverse_to_eh(value):
    """
    Convert the *value* in unit :math:`\\text{cm}^{-1}` to hartree.

    :param value: The value to be converted.
    :return: The converted value.
    """
    return value / EH_M_INVERSE * 100


@vectorize([float64(float64)], nopython=True, cache=True, target=_target)
def ev_to_m_inverse(value):
    """
    Convert the *value* in unit electronvolt to :math:`\\text{m}^{-1}`.

    :param value: The value to be converted.
    :return: The converted value.
    """
    return value * EV_M_INVERSE


@vectorize([float64(float64)], nopython=True, cache=True, target=_target)
def m_inverse_to_ev(value):
    """
    Convert the *value* in unit :math:`\\text{m}^{-1}` to electronvolt.

    :param value: The value to be converted.
    :return: The converted value.
    """
    return value / EV_M_INVERSE


@vectorize([float64(float64)], nopython=True, cache=True, target=_target)
def ev_to_cm_inverse(value):
    """
    Convert the *value* in unit electronvolt to :math:`\\text{cm}^{-1}`.

    :param value: The value to be converted.
    :return: The converted value.
    """
    return value * EV_M_INVERSE / 100


@vectorize([float64(float64)], nopython=True, cache=True, target=_target)
def cm_inverse_to_ev(value):
    """
    Convert the *value* in unit :math:`\\text{cm}^{-1}` to electronvolt.

    :param value: The value to be converted.
    :return: The converted value.
    """
    return value / EV_M_INVERSE * 100


@vectorize([float64(float64)], nopython=True, cache=True, target=_target)
def ev_to_k(value):
    """
    Convert the *value* in unit electronvolt to kelvin.

    :param value: The value to be converted.
    :return: The converted value.
    """
    return value * EV_K


@vectorize([float64(float64)], nopython=True, cache=True, target=_target)
def k_to_ev(value):
    """
    Convert the *value* in unit kelvin to electronvolt.

    :param value: The value to be converted.
    :return: The converted value.
    """
    return value / EV_K


@vectorize([float64(float64)], nopython=True, cache=True, target=_target)
def ry_to_j(value):
    """
    Convert the *value* in unit rydberg to joule.

    :param value: The value to be converted.
    :return: The converted value.
    """
    return value * RY_J


@vectorize([float64(float64)], nopython=True, cache=True, target=_target)
def j_to_ry(value):
    """
    Convert the *value* in unit joule to rydberg.

    :param value: The value to be converted.
    :return: The converted value.
    """
    return value / RY_J


@vectorize([float64(float64)], nopython=True, cache=True, target=_target)
def gpa_to_ev_a3(value):
    """
    Convert the *value* in unit gigapascal to :math:`\\frac{ \\text{electronvolt} }{ \\text{angstrom}^3 }`.

    :param value: The value to be converted.
    :return: The converted value.
    """
    return value * 1e9 / electron_volt * angstrom ** 3


@vectorize([float64(float64)], nopython=True, cache=True, target=_target)
def ev_a3_to_gpa(value):
    """
    Convert the *value* in unit :math:`\\frac{ \\text{electronvolt} }{ \\text{angstrom}^3 }` to gigapascal.

    :param value: The value to be converted.
    :return: The converted value.
    """
    return value / 1e9 * electron_volt / angstrom ** 3


@vectorize([float64(float64)], nopython=True, cache=True, target=_target)
def gpa_to_ev_b3(value):
    """
    Convert the *value* in unit gigapascal to :math:`\\frac{ \\text{electronvolt} }{ \\text{bohr radius}^3 }`.

    :param value: The value to be converted.
    :return: The converted value.
    """
    return value * 1e9 / electron_volt * BOHR ** 3


@vectorize([float64(float64)], nopython=True, cache=True, target=_target)
def ev_b3_to_gpa(value):
    """
    Convert the *value* in unit :math:`\\frac{ \\text{electronvolt} }{ \\text{bohr radius}^3 }` to gigapascal.

    :param value: The value to be converted.
    :return: The converted value.
    """
    return value / 1e9 * electron_volt / BOHR ** 3


@vectorize([float64(float64)], nopython=True, cache=True, target=_target)
def gpa_to_ry_b3(value):
    """
    Convert the *value* in unit gigapascal to :math:`\\frac{ \\text{rydberg} }{ \\text{bohr radius}^3 }`.

    :param value: The value to be converted.
    :return: The converted value.
    """
    return value * 1e9 / RY_J * BOHR ** 3


@vectorize([float64(float64)], nopython=True, cache=True, target=_target)
def ry_b3_to_gpa(value):
    """
    Convert the *value* in unit :math:`\\frac{ \\text{rydberg} }{ \\text{bohr radius}^3 }` to gigapascal.

    :param value: The value to be converted.
    :return: The converted value.
    """
    return value / 1e9 * RY_J / BOHR ** 3


@vectorize([float64(float64)], nopython=True, cache=True, target=_target)
def gpa_to_ha_b3(value):
    """
    Convert the *value* in unit gigapascal to :math:`\\frac{ \\text{hartree} }{ \\text{bohr radius}^3 }`.

    :param value: The value to be converted.
    :return: The converted value.
    """
    return value * 1e9 / RY_J * BOHR ** 3 / 2


@vectorize([float64(float64)], nopython=True, cache=True, target=_target)
def ha_b3_to_gpa(value):
    """
    Convert the *value* in unit :math:`\\frac{ \\text{hartree} }{ \\text{bohr radius}^3 }` to gigapascal.

    :param value: The value to be converted.
    :return: The converted value.
    """
    return 2 * value / 1e9 * RY_J / BOHR ** 3


@vectorize([float64(float64)], nopython=True, cache=True, target=_target)
def ry_b_to_ev_a(value):
    """
    The atomic force.
    Convert the *value* in unit :math:`\\frac{ \\text{rydberg} }{ \\text{bohr radius} }` to
    :math:`\\frac{ \\text{electronvolt} }{ \\text{angstrom} }`.

    :param value: The value to be converted.
    :return: The converted value.
    """
    return value * RY_EV / (BOHR / angstrom)


@vectorize([float64(float64)], nopython=True, cache=True, target=_target)
def ha_b_to_ev_a(value):
    """
    The atomic force.
    Convert the *value* in unit :math:`\\frac{ \\text{hartree} }{ \\text{bohr radius} }` to
    :math:`\\frac{ \\text{electronvolt} }{ \\text{angstrom} }`.

    :param value: The value to be converted.
    :return: The converted value.
    """
    return value * EH_EV / (BOHR / angstrom)


@vectorize([float64(float64)], nopython=True, cache=True, target=_target)
def ry_to_kj_mol(value):
    """
    Convert the *value* is in unit Rydberg, the converted value is in unit
    :math:`\\frac{ \\text{k J} }{ \\text{mol} }`.

    :param value: The value to be converted.
    :return: the converted value.
    """
    return value * Avogadro * RY_J / 1000


@vectorize([float64(float64)], nopython=True, cache=True, target=_target)
def ry_to_j_mol(value):
    """
    Convert the *value* is in unit Rydberg, the converted value is in unit
    :math:`\\frac{ \\text{k J} }{ \\text{mol} }`.

    :param value: The value to be converted.
    :return: the converted value.
    """
    return value * Avogadro * RY_J
