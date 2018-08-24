Prepare the input: ``qha convert``
**********************************

If the user has used `Quantum ESPRESSO <https://www.quantum-espresso.org>`_,
he/she might have the phonon frequency file(s) from the program ``matdyn.x``.
To generate a valid input data file for ``qha``, three  files are needed:

1. ``filelist.yaml`` file:

* the description of the system in ``comment`` key: a string,
* the number of formula unit in ``formula_unit_number`` key: an integer,
* A YAML list of files containing frequencies ``*.freq`` in ``frequency_files`` key: a YAML list of strings.

  If you have trouble writing YAML, please refer to its syntax `here <http://docs.ansible.com/ansible/latest/reference_appendices/YAMLSyntax.html>`_.

2. An ``static`` file that contains the static energies and volumes for
   each configuration.
3. An ``q_points`` file that specifies all the q-points to sample
   the Brillouin zone. The first three columns are the q-points' coordinates in 3D space, and
   the last column is their weights.


Please check the ``/examples/silicon/make_input`` as an example.

When all these files are obtained, put them in them same directory and run::

   $ qha-convert filelist.yaml static q_points

then a file named ``input`` will be generated in the same directory.
