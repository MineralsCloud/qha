Run calculation command: ``qha run``
************************************

.. contents:: Table of contents:
   :local:

How to write computational settings file
========================================

First one needs to prepare a standard input file and a YAML file specifying
the computational settings, which is referred to ``settings.yaml`` here.
Please refer to `this website <https://docs.ansible.com/ansible/latest/reference_appendices/YAMLSyntax.html>`_
if not familiar with YAML syntax.

Here are the keys that can be recognized in ``settings.yaml``:

* ``calculation``: The calculation type user wants to perform. Allowed values are ``single``, ``same phonon dos`` and ``different phonon dos``.
* ``NT``: Number of temperatures on the grid
* ``DT``: The interval between two nearest temperatures on the grid
* ``NTV``: Number of volumes (or equivalently, pressure) on the gird
* ``DELTA_P``: The interval between two pressures on the grid, the default value is :math:`0.1` GPa
* ``DELTA_P_SAMPLE``: Pressure-sampling interval, used for output, the default value is :math:`1` GPa
* ``P_MIN``: Desired minimum pressure to calculate, in GPa
* ``input``: Name(s) of the input file(s).

  * In the single-configuration calculation, only the path of the file is needed,
  * In the multi-configuration calculation, the names of the inputs files and the corresponding configuration degeneracy are given in a `YAML dictionary syntax <https://docs.ansible.com/ansible/latest/plugins/lookup/dict.html>`_.

* ``static_only``: Whether to include the vibrational contribution in the calculation. Allowed values are ``True`` (not include) or ``False`` (include, default).
* ``order``: Order of Birch–Murnaghan equation of state fitting, can be ``3`` (default), ``4`` or ``5``.
* ``energy_unit``: Energy unit in the output file can be ``ry`` (default) or ``ev``
* ``thermodynamic_properties``: Which thermodynamic properties will be calculated by ``qha``. Allowed values are

  * ``F``: the Helmholtz free energy
  * ``G``: the Gibbs free energy
  * ``U``: the internal energy
  * ``H``: the enthalpy
  * ``V``: the volume
  * ``Cp``: the pressure specific heat capacity
  * ``Cv``: the volumetric specific heat capacity
  * ``Bt``: the isothermal bulk modulus
  * ``Btp``: the derivative of the isothermal bulk modulus with respect to pressure
  * ``Bs``: the adiabatic bulk modulus
  * ``alpha``: the thermal expansion coefficient
  * ``gamma``: the Grüneisen parameter

* ``target``: The default value is ``parallel``.
  This is a Numba package option. Allowed options are ``cpu`` (used on single-threaded CPU), ``parallel`` (used on multi-core CPU), and ``cuda`` (used on CUDA GPU).
  See its `official documentation <http://numba.pydata.org/numba-doc/0.39.0/reference/jit-compilation.html#numba.vectorize>`_ for help.
* ``results_folder``: The path to store all calculated values, the default value is ``./results``, which is a directory named `results` in
  the same folder as the ``input`` file.
* ``plot_results``: Plot all thermodynamic properties in PDF format, allowed values are ``True`` or ``False`` (default).
* ``T4FV``: Temperature for :math:`F(T_i, V)` plotting. ``['0', '300']`` by default.
* ``high_verbosity``: Two verbosity levels are implemented in the output file, ``True`` or ``False`` (default).

How to make input data
======================

The input format is as below:

.. image:: ../_static/input_format.png
   :width: 800 px
   :align: center

After one has prepared ``settings.yaml`` and ``input`` in the same directory,
just open the terminal, redirect to that directory and run::

   $ qha run ./settings.yaml

then the results will be generated in the directory specified
in ``results_folder`` option in ``settings.yaml``.
If the ``settings.yaml`` is not in the same directory as the input file, one has to explicitly specify the
path of it on his/her computer.


Output
======

The output files' names and their meanings are as below:

* Helmholtz free energy: ``f_tp_ry.txt`` or ``f_tp_ev.txt``
* Gibbs free energy: ``g_tp_ry.txt`` or ``g_tp_ev.txt``
* Enthalpy: ``h_tp_ry.txt`` or ``h_tp_ev.txt``
* Volume: ``v_tp_bohr3.txt`` or ``v_tp_ang3.txt``
* Pressure-specific heat capacity: ``cp_tp_jmolk.txt``
* Volume-specific heat capacity: ``cv_tp_jmolk.txt``
* Isothermal bulk modulus: ``bt_tp_gpa.txt``
* Derivative of the isothermal bulk modulus with
  respect to pressure: ``btp_tp.txt``
* Adiabatic bulk modulus: ``bs_tp_gpa.txt``
* Thermal expansion: ``alpha_tp.txt``
* Thermal Grüneisen parameters: ``gamma_tp.txt``
