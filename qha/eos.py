#!/usr/bin/env python3
"""
:mod:`eos` -- equation of states
================================

.. module eos
   :platform: Unix, Windows, Mac, Linux
   :synopsis: Referenced from `here <https://wiki.fysik.dtu.dk/ase/_modules/ase/eos.html#EquationOfState>`_.
.. moduleauthor:: Qi Zhang <qz2280@columbia.edu>
"""

from abc import abstractmethod
from typing import Optional, Dict, Callable

import numpy as np
from numba import jit
from scipy.optimize import fsolve

# ===================== What can be exported? =====================
__all__ = [
    'parabola', 'birch', 'murnaghan', 'birch_murnaghan3rd', 'pourier_tarantola', 'vinet',
    'EOS', 'Birch', 'Murnaghan', 'BirchMurnaghan3rd', 'PourierTarantola', 'Vinet',
    'SIMPLE_EOS', 'VERSATILE_EOS', 'simple_eos', 'versatile_eos'
]


# ! Note this module is currently not used.

@jit(nopython=True)
def parabola(v: float, a: float, b: float, c: float) -> float:
    """parabola polynomial function :math:`c v^2 + b v + a`.

    This function is used to fit the data to get good guesses for
    the equation of state fits.
    A 2nd order seems to be sufficient, and guarantees a single minimum.

    :param v: Volume at which free energy is to be calculated.
    :param a: Constant.
    :param b: Coefficient of linear term.
    :param c: Coefficient of 2nd-order term.
    :return: The calculated free energy at volume *v*.
    """
    if c == 0:
        raise ValueError(
            "Argument *c* cannot be 0! Because it is the coefficient of 2nd-order term!")
    return a + b * v + c * v ** 2


@jit(nopython=True)
def birch(v: float, b0: float, bp0: float, v0: float, f0: Optional[float] = 0) -> float:
    """
    Calculate free energy at volume *v*, according to Birch EoS. [#b]_

    .. [#b] From "Intermetallic compounds: Principles and Practice, Vol. I: Principles Chapter 9 pages 195-210 by M. Mehl. B. Klein, D. Papaconstantopoulos", case where :math:`n=0`.

    :param v: Volume at which free energy is to be calculated.
    :param b0: Bulk modulus at zero-pressure, as a reference parameter for the EoS.
    :param bp0: Bulk modulus's first order derivative W.R.T pressure at zero-pressure, as a reference parameter for the EoS.
    :param v0: Zero-pressure volume for the system.
    :param f0: The baseline of free energy, defaults to :math:`0`.
    :return: The calculated free energy at volume *v*.
    """
    x = (v0 / v) ** (2 / 3) - 1
    xi = 9 / 16 * b0 * v0 * x ** 2
    return f0 + 2 * xi + (bp0 - 4) * xi * x


@jit(nopython=True)
def murnaghan(v: float, b0: float, bp0: float, v0: float, f0: Optional[float] = 0):
    """
    Calculate free energy at volume *v*, according to Murnaghan EoS. [#m]_

    .. [#m] From PRB 28,5480 (1983).

    :param v: Volume at which free energy is to be calculated.
    :param b0: Bulk modulus at zero-pressure, as a reference parameter for the EoS.
    :param bp0: Bulk modulus's first order derivative W.R.T pressure at zero-pressure, as a reference parameter for the EoS.
    :param v0: Zero-pressure volume for the system.
    :param f0: The baseline of free energy, defaults to :math:`0`.
    :return: The calculated free energy at volume *v*.
    """
    x = bp0 - 1
    y = (v0 / v) ** bp0
    return f0 + b0 / bp0 * v * (y / x + 1) - v0 * b0 / x


@jit(nopython=True)
def birch_murnaghan3rd(v: float, b0: float, bp0: float, v0: float, f0: Optional[float] = 0):
    """
    Calculate free energy at volume *v*, according to Birch-Murnaghan third-order EoS. [#bm]_

    .. [#bm] BirchMurnaghan equation from PRB 70, 224107 Eq. (3) in the paper. Note that there's a typo in the paper and it uses inverted expression for eta.

    :param v: Volume at which free energy is to be calculated.
    :param b0: Bulk modulus at zero-pressure, as a reference parameter for the EoS.
    :param bp0: Bulk modulus's first order derivative W.R.T pressure at zero-pressure, as a reference parameter for the EoS.
    :param v0: Zero-pressure volume for the system.
    :param f0: The baseline of free energy, defaults to :math:`0`.
    :return: The calculated free energy at volume *v*.
    """
    eta = (v0 / v) ** (1 / 3)
    xi = eta ** 2 - 1
    return f0 + 9 / 16 * b0 * v0 * xi ** 2 * (6 + bp0 * xi - 4 * eta ** 2)


@jit(nopython=True)
def pourier_tarantola(v: float, b0: float, bp0: float, v0: float, f0: Optional[float] = 0):
    """
    Calculate free energy at volume *v*, according to Pourier-Tarantola EoS. [#pt]_

    .. [#pt] Pourier-Tarantola's equation from PRB 70, 224107.

    ::param v: Volume at which free energy is to be calculated.
    :param b0: Bulk modulus at zero-pressure, as a reference parameter for the EoS.
    :param bp0: Bulk modulus's first order derivative W.R.T pressure at zero-pressure, as a reference parameter for the EoS.
    :param v0: Zero-pressure volume for the system.
    :param f0: The baseline of free energy, defaults to :math:`0`.
    :return: The calculated free energy at volume *v*.
    """
    x = (v / v0) ** (1 / 3)
    squiggle = -3 * np.log(x)
    return f0 + b0 * v0 * squiggle ** 2 / 6 * (3 + squiggle * (bp0 - 2))


@jit(nopython=True)
def vinet(v: float, b0: float, bp0: float, v0: float, f0: Optional[float] = 0):
    """
    Calculate free energy at volume *v*, according to Vinet EoS. [#v]_

    .. [#v] Vinet equation from PRB 70, 224107. It is equivalent to the equation in
    Poirier, Jean-Paul. *Introduction to the Physics of the Earth's Interior*. Cambridge University Press, 2000.

    :param v: Volume at which free energy is to be calculated.
    :param b0: Bulk modulus at zero-pressure, as a reference parameter for the EoS.
    :param bp0: Bulk modulus's first order derivative W.R.T pressure at zero-pressure, as a reference parameter for the EoS.
    :param v0: Zero-pressure volume for the system.
    :param f0: The baseline of free energy, defaults to :math:`0`.
    :return: The calculated free energy at volume *v*.
    """
    x = (v / v0) ** (1 / 3)
    xi = 3 / 2 * (bp0 - 1)
    return f0 + 9 * b0 * v0 / xi ** 2 * (1 + (xi * (1 - x) - 1) * np.exp(xi * (1 - x)))


class EOS:
    """
    An abstract base class for equations of states.

    :param b0: Bulk modulus at zero-pressure, as a reference parameter for the EoS.
    :param bp0: Bulk modulus's first order derivative W.R.T pressure at zero-pressure, as a reference parameter for the EoS.
    :param v0: Zero-pressure volume for the system.
    :param f0: The baseline of free energy, defaults to :math:`0`.
    """

    def __init__(self, b0: float, bp0: float, v0: float, f0: Optional[float] = 0):
        self.b0 = b0
        self.bp0 = bp0
        self.v0 = v0
        self.f0 = f0

    @abstractmethod
    def free_energy_at(self, v: float) -> float:
        """
        Evaluate free energy at volume *v*, according to the equation of state of free energy.

        :param v: Volume at which free energy is to be evaluated.
        :return: The calculated free energy.
        """
        pass

    @abstractmethod
    def pressure_at(self, v: float) -> float:
        """
        Evaluate pressure at volume *v*, according to the equation of state of pressure.

        :param v: Volume at which pressure is to be evaluated.
        :return: The calculated pressure.
        """
        pass

    def solve_v_by_p(self, p: float, v_guess: float):
        """
        Solve the pressure, according to the equation of state of pressure, an initial guess *v_guess* is required.

        :param p: The pressure at which the volume is to be worked out.
        :param v_guess: An initial guess for ``scipy.optimize.fsovle``.
        """
        return fsolve(lambda v: self.pressure_at(v) - p, np.array(v_guess))


class Birch(EOS):
    def free_energy_at(self, v: float) -> float:
        x = (self.v0 / v) ** (2 / 3) - 1
        xi = 9 / 16 * self.b0 * self.v0 * x ** 2
        return self.f0 + 2 * xi + (self.bp0 - 4) * xi * x

    def pressure_at(self, v: float) -> float:
        x = self.v0 / v
        xi = x ** (2 / 3) - 1
        return 3 / 8 * self.b0 * x ** (5 / 3) * xi * (4 + 3 * (self.bp0 - 4) * xi)


class Murnaghan(EOS):
    def free_energy_at(self, v: float) -> float:
        x = self.bp0 - 1
        y = (self.v0 / v) ** self.bp0
        return self.f0 + self.b0 / self.bp0 * v * (y / x + 1) - self.v0 * self.b0 / x

    def pressure_at(self, v: float) -> float:
        return self.b0 / self.bp0 * ((self.v0 / v) ** self.bp0 - 1)


class BirchMurnaghan3rd(EOS):
    def free_energy_at(self, v: float) -> float:
        eta = (self.v0 / v) ** (1 / 3)
        xi = eta ** 2 - 1
        return self.f0 + 9 / 16 * self.b0 * self.v0 * xi ** 2 * (6 + self.bp0 * xi - 4 * eta ** 2)

    def pressure_at(self, v: float) -> float:
        eta = (self.v0 / v) ** (1 / 3)
        return 3 / 2 * self.b0 * (eta ** 7 - eta ** 5) * (1 + 3 / 4 * (self.bp0 - 4) * (eta ** 2 - 1))


class PourierTarantola(EOS):
    def free_energy_at(self, v: float) -> float:
        x = (v / self.v0) ** (1 / 3)
        squiggle = -3 * np.log(x)
        return self.f0 + self.b0 * self.v0 * squiggle ** 2 / 6 * (3 + squiggle * (self.bp0 - 2))

    def pressure_at(self, v: float) -> float:
        x = np.log(v / self.v0)
        return self.b0 * self.v0 / 2 / v * x * ((self.bp0 - 2) * x - 2)


class Vinet(EOS):
    def free_energy_at(self, v: float) -> float:
        x = (v / self.v0) ** (1 / 3)
        xi = 3 / 2 * (self.bp0 - 1)
        return self.f0 + 9 * self.b0 * self.v0 / xi ** 2 * (1 + (xi * (1 - x) - 1) * np.exp(xi * (1 - x)))

    def pressure_at(self, v: float) -> float:
        x = (v / self.v0) ** (1 / 3)
        xi = 3 / 2 * (self.bp0 - 1)
        return 3 * self.b0 / x ** 2 * (1 - x) * np.exp(xi * (1 - x))


SIMPLE_EOS: Dict[str, Callable] = {
    'm': murnaghan,
    'b-m': birch_murnaghan3rd,
    'p-t': pourier_tarantola,
    'v': vinet,
    'b': birch
}


def simple_eos(name: str) -> Callable:
    """
    A function that collects severl EoSs for free energy calculation. The only allowed keys
    are one of "m" (Murnaghan), "b-m" (Birch Murnaghan 3rd-order), "p-t" (Pourier Tarantola), "v" (Vinet), "b" (Birch).
    See the documentations of ``murnaghan``, ``birch_murnaghan3rd``, ``pourier_tarantola``, ``vinet``,
    and ``birch`` for details.
    """
    return SIMPLE_EOS[name]


VERSATILE_EOS = {
    'b': Birch,
    'm': Murnaghan,
    'b-m': BirchMurnaghan3rd,
    'p-t': PourierTarantola,
    'v': Vinet,
}


def versatile_eos(name: str) -> Callable:
    """
    A more powerful collection of EoSs that can calculate free energies, pressures, and solve volumes by given pressures.
    The only *name* allowed
    is one of "m" (Murnaghan), "b-m" (Birch Murnaghan 3rd-order), "p-t" (Pourier Tarantola), "v" (Vinet), "b" (Birch).
    See the documentations of ``Birch``, ``Murnaghan``, ``BirchMurnaghan3rd``, ``PourierTarantola``,
    and ``Vinet`` for details.
    """
    return VERSATILE_EOS[name]
