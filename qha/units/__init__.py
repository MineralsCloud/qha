import pint
from scipy.constants import physical_constants

__all__ = ['QHAUnits']

def define_units(ureg: pint.UnitRegistry):
    ureg.define('Bohr = %s m = bohr' % (
        repr(physical_constants['Bohr radius'][0])
    ))

    ureg.define('Rydberg = %s eV = Ryd = Ry = ry = ryd' % (
        repr(physical_constants['Rydberg constant times hc in eV'][0])
    ))

class QHAUnits(object):
    __instance = None
    def __new__(cls):
        if QHAUnits.__instance is None:
            QHAUnits.__instance = pint.UnitRegistry()
        define_units(QHAUnits.__instance)
        return QHAUnits.__instance