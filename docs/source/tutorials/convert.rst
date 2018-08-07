Prepare the input: ``qha convert``
**********************************

If the user has used `Quantum ESPRESSO <https://www.quantum-espresso.org>`_,
he/she might have the phonon frequency file(s) from the program ``matdyn.x``.
To generate a valid input data file for ``qha``, one needs two more files:

1. An ``inp_q_points`` file that specifies all the q-points to sample
   the Brillouin zone. The first three columns are the q-points' coordinates in 3D space, and
   the last column is their weights.
2. An ``inp_static`` file that contains the static energies and volumes for
   each configuration.

When all these files are obtained, put them in them same directory and run::

   $ qha-convert <inp_file_list> <inp_static> <inp_q_points>

then a file named ``input`` will be generated in the same directory.
