Prepare input command: ``qha-convert``
**************************************

If you have used `Quantum ESPRESSO <https://www.quantum-espresso.org>`_,
you might have the phonon frequency file from `matdyn.x`. If you want
to use it to generate a valid input data file for ``qha``, you need
two more files:

1. A ``inp_q_points`` file that specifies all the q-points you want to sample
   in the Brillouin zone. The first three columns are their coordinates, and
   the last column is the weights of each q-point.
2. A ``inp_static`` file that contains the static energies and volumes for
   each configuration.

When you have all of these files, put them in them same directory and run::

   $ qha-convert <inp_file_list> <inp_static> <inp_q_points>

and the a file named ``input`` will be generated in the same directory.
