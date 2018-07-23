#!/usr/bin/env python3


from lazy_property import LazyProperty

import qha.tools
from qha.thermodynamics import *
from qha.utils.units import QHAUnits
from qha.v2p import v2p
from .helmholtz_calculator import HelmholtzFreeEnergyCalculator

units = QHAUnits()

__all__ = [
    'TemperaturePressureFieldAdapter'
]


class TemperaturePressureFieldAdapter:
    def __init__(self, calculator: HelmholtzFreeEnergyCalculator):
        self.calculator = calculator
        # self.calculator.bind_pressure_adapter(self)
        self._settings = self.calculator.settings

    def validate(self):
        self.validate_pressure_array_in_interplotation_range()

    def validate_pressure_array_in_interplotation_range(self) -> None:
        # TODO: Maybe should in adapter
        d = self.settings
        p_tv_gpa = self.calculator.pressures.to(units.GPa).magnitude
        desired_pressures_gpa = self.pressure_array.to(units.GPa).magnitude

        '''

        # TODO: Should not write output here
        if d['high_verbosity']:
            save_to_output(d['qha_output'], "The pressure range can be dealt with: [{0:6.2f} to {1:6.2f}] GPa".format(
                p_tv_gpa[:, 0].max(),
                p_tv_gpa[:, -1].min()
            ))
        '''

        if p_tv_gpa[:, -1].min() < desired_pressures_gpa.max():
            ntv_max = int((p_tv_gpa[:, -1].min() - desired_pressures_gpa.min()) / d['DELTA_P'])

            '''
            save_to_output(d['qha_output'], textwrap.dedent("""\
                           !!!ATTENTION!!!
                           
                           DESIRED PRESSURE is too high (NTV is too large)!
                           QHA results might not be right!
                           Please reduce the NTV accordingly, for example, try to set NTV < {:4d}.
                           """.format(ntv_max)))
            '''

            raise ValueError("DESIRED PRESSURE is too high (NTV is too large), qha results might not be right!")

    @property
    def settings(self): return self.calculator.settings

    def __convert_to_pressure_field(self, volume_field):
        return v2p(
            volume_field,
            self.calculator.pressures.magnitude,
            self.pressure_array.magnitude
        )

    @LazyProperty
    def formula_unit_number(self):
        return self.calculator.formula_unit_number

    @LazyProperty
    @units.wraps(units.kelvin, None)
    def temperature_array(self):
        return self.calculator.temperature_array.magnitude

    @LazyProperty
    @units.wraps(units.Ryd / units.Bohr ** 3, None)
    def pressure_array(self):
        return units.Quantity(
            qha.tools.arange(
                self.settings['P_MIN'],
                self.settings['NTV'],
                self.settings['DELTA_P']
            ),
            units.GPa
        ).to(units.Ryd / units.Bohr ** 3).magnitude

    @LazyProperty
    @units.wraps(units.Ryd, None)
    def helmholtz_free_energies(self):
        return self.__convert_to_pressure_field(
            self.calculator.helmholtz_free_energies.magnitude
        )

    @LazyProperty
    @units.wraps(units.Ryd, None)
    def gibbs_free_energies(self):
        return self.__convert_to_pressure_field(
            self.calculator.gibbs_free_energies.magnitude
        )

    @LazyProperty
    @units.wraps(units.Ryd, None)
    def internal_energies(self):
        return self.__convert_to_pressure_field(
            self.calculator.internal_energies.magnitude
        )

    @LazyProperty
    @units.wraps(units.Ryd, None)
    def entropies(self):
        return self.__convert_to_pressure_field(
            self.calculator.entropies.magnitude
        )

    @LazyProperty
    @units.wraps(units.Ryd / units.kelvin, None)
    def volume_specific_heat_capacities(self):
        return self.__convert_to_pressure_field(
            self.calculator.volume_specific_heat_capacities.magnitude
        )

    @LazyProperty
    @units.wraps(units.Ryd / units.kelvin, None)
    def pressure_specific_heat_capacities(self):
        return pressure_specific_heat_capacity(
            self.temperature_array.magnitude,
            self.entropies.magnitude
        )

    @LazyProperty
    @units.wraps(units.Ryd / units.Bohr ** 3, None)
    def isothermal_bulk_moduli(self):
        return self.__convert_to_pressure_field(
            self.calculator.isothermal_bulk_moduli.magnitude
        )

    @LazyProperty
    @units.wraps(units.Ryd / units.Bohr ** 3, None)
    def adiabatic_bulk_moduli(self):
        return adiabatic_bulk_modulus(
            self.isothermal_bulk_moduli.magnitude,
            self.thermal_expansion_coefficients.magnitude,
            self.gruneisen_parameters.magnitude,
            self.temperature_array.magnitude
        )

    @LazyProperty
    @units.wraps(units.dimensionless, None)
    def gruneisen_parameters(self):
        return gruneisen_parameter(
            self.volumes.magnitude,
            self.isothermal_bulk_moduli.magnitude,
            self.thermal_expansion_coefficients.magnitude,
            self.calculator.volume_specific_heat_capacities.magnitude
        )

    @LazyProperty
    @units.wraps(units.kelvin ** -1, None)
    def thermal_expansion_coefficients(self):
        return thermal_expansion_coefficient(
            self.temperature_array.magnitude,
            self.volumes.magnitude
        )

    @LazyProperty
    @units.wraps(units.dimensionless, None)
    def isothermal_bulk_modulus_pressure_derivatives(self):
        return bulk_modulus_derivative(
            self.pressure_array.magnitude,
            self.isothermal_bulk_moduli.magnitude
        )

    @LazyProperty
    @units.wraps(units.Bohr ** 3, None)
    def volumes(self):
        return volume_tp(
            self.calculator.volume_array.magnitude,
            self.pressure_array.magnitude,
            self.calculator.pressures.magnitude
        )
