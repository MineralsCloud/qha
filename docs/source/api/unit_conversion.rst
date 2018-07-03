Fast unit conversion functions
********************************

Nearly all the functions in this module have been speeduped by `Numba <https://numba.pydata.org>`_ package,
which means they are fast, but the input argument must be of type ``float``.

.. automodule:: qha

.. automodule:: qha.utils.unit_conversion

   .. autofunction:: j_to_ev(value)
   .. autofunction:: ev_to_j(value)
   .. autofunction:: gpa_to_megabar(value)
   .. autofunction:: megabar_to_gpa(value)
   .. autofunction:: b3_to_a3(value)
   .. autofunction:: a3_to_b3(value)
   .. autofunction:: eh_to_ev(value)
   .. autofunction:: ev_to_eh(value)
   .. autofunction:: ry_to_ev(value)
   .. autofunction:: ev_to_ry(value)
   .. autofunction:: j_to_eh(value)
   .. autofunction:: eh_to_j(value)
   .. autofunction:: eh_to_hz(value)
   .. autofunction:: hz_to_eh(value)
   .. autofunction:: eh_to_k(value)
   .. autofunction:: k_to_eh(value)
   .. autofunction:: eh_to_m_inverse(value)
   .. autofunction:: m_inverse_to_eh(value)
   .. autofunction:: eh_to_cm_inverse(value)
   .. autofunction:: cm_inverse_to_eh(value)
   .. autofunction:: ev_to_m_inverse(value)
   .. autofunction:: m_inverse_to_ev(value)
   .. autofunction:: ev_to_cm_inverse(value)
   .. autofunction:: cm_inverse_to_ev(value)
   .. autofunction:: ev_to_k(value)
   .. autofunction:: k_to_ev(value)
   .. autofunction:: ry_to_j(value)
   .. autofunction:: j_to_ry(value)
   .. autofunction:: gpa_to_ev_a3(value)
   .. autofunction:: ev_a3_to_gpa(value)
   .. autofunction:: gpa_to_ry_b3(value)
   .. autofunction:: ry_b3_to_gpa(value)
   .. autofunction:: gpa_to_ha_b3(value)
   .. autofunction:: ha_b3_to_gpa(value)
   .. autofunction:: ev_b3_to_gpa(value)
   .. autofunction:: gpa_to_ev_b3(value)
   .. autofunction:: ry_b_to_ev_a(value)
   .. autofunction:: ha_b_to_ev_a(value)
   .. autofunction:: ry_to_kj_mol(value)
   .. autofunction:: ry_to_j_mol(value)
