# %%
from qha.calculator import Calculator, SamePhDOSCalculator, DifferentPhDOSCalculator
from qha.basic_io.out import (
    save_x_tp,
    save_x_tv,
    save_to_output,
    make_starting_string,
    make_tp_info,
    make_ending_string,
)
from qha.settings import from_yaml
from qha.thermodynamics import *

# %%
user_settings = {}
file_settings = "settings.yaml"
settings = from_yaml(file_settings)

for key in (
    "input",
    "calculation",
    "thermodynamic_properties",
    "static_only",
    "energy_unit",
    "T_MIN",
    "NT",
    "DT",
    "DT_SAMPLE",
    "P_MIN",
    "NTV",
    "DELTA_P",
    "DELTA_P_SAMPLE",
    "volume_ratio",
    "order",
    "p_min_modifier",
    "T4FV",
    "output_directory",
    "high_verbosity",
):
    try:
        user_settings.update({key: settings[key]})
    except KeyError:
        continue

# %%
calculation_type = user_settings["calculation"].lower()
if calculation_type == "single":
    calc = Calculator(user_settings)
    print("You have single-configuration calculation assumed.")
elif calculation_type == "same phonon dos":
    calc = SamePhDOSCalculator(user_settings)
    print("You have multi-configuration calculation with the same phonon DOS assumed.")
elif calculation_type == "different phonon dos":
    calc = DifferentPhDOSCalculator(user_settings)
    print("You have multi-configuration calculation with different phonon DOS assumed.")
else:
    raise ValueError(
        "The 'calculation' in your settings in not recognized! It must be one of:"
        "'single', 'same phonon dos', 'different phonon dos'!"
    )

# %%
calc.read_input()

# %%
calc.vib_ry()

# %%
calc.refine_grid()

# %%
calc.thermodynamic_potentials()

# %%
# calc.cv_tv_au()

# %%
calc.cp_tp_jmolk()

# %%
# calc.f_tp_ry()

# # %%
# calc.bt_tv_au()

# # %%
# calc.bt_tp_au()

# # %%
# calc.bt_tp_gpa()

# # %%
# calc.alpha_tp()


