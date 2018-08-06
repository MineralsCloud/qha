Fast unit conversion functions
********************************

Nearly all the functions in this module have been speeduped by `Numba <https://numba.pydata.org>`_ package,
which means they are fast, but the input argument must be of type ``float``.

.. automodule:: qha

.. automodule:: qha.unit_conversion

   .. autofunction:: j_to_ev
   .. autofunction:: ev_to_j
   .. autofunction:: gpa_to_megabar
   .. autofunction:: megabar_to_gpa
   .. autofunction:: b3_to_a3
   .. autofunction:: a3_to_b3
   .. autofunction:: eh_to_ev
   .. autofunction:: ev_to_eh
   .. autofunction:: ry_to_ev
   .. autofunction:: ev_to_ry
   .. autofunction:: j_to_eh
   .. autofunction:: eh_to_j
   .. autofunction:: eh_to_hz
   .. autofunction:: hz_to_eh
   .. autofunction:: eh_to_k
   .. autofunction:: k_to_eh
   .. autofunction:: eh_to_m_inverse
   .. autofunction:: m_inverse_to_eh
   .. autofunction:: eh_to_cm_inverse
   .. autofunction:: cm_inverse_to_eh
   .. autofunction:: ev_to_m_inverse
   .. autofunction:: m_inverse_to_ev
   .. autofunction:: ev_to_cm_inverse
   .. autofunction:: cm_inverse_to_ev
   .. autofunction:: ev_to_k
   .. autofunction:: k_to_ev
   .. autofunction:: ry_to_j
   .. autofunction:: j_to_ry
   .. autofunction:: gpa_to_ev_a3
   .. autofunction:: ev_a3_to_gpa
   .. autofunction:: gpa_to_ry_b3
   .. autofunction:: ry_b3_to_gpa
   .. autofunction:: gpa_to_ha_b3
   .. autofunction:: ha_b3_to_gpa
   .. autofunction:: ev_b3_to_gpa
   .. autofunction:: gpa_to_ev_b3
   .. autofunction:: ry_b_to_ev_a
   .. autofunction:: ha_b_to_ev_a
   .. autofunction:: ry_to_kj_mol
   .. autofunction:: ry_to_j_mol
